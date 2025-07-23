import json
from flask import Blueprint, request, jsonify, Response, stream_with_context, send_file
from .models import Story, StoryPage
from . import story_generator
from .utils import create_story_pdf
from .extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from threading import Lock

main_bp = Blueprint('main_bp', __name__)

# This lock prevents the 20-page bug
generation_locks = {}
story_lock = Lock()

@main_bp.route('/chat', methods=['POST'])
@jwt_required()
def handle_chat():
    data = request.get_json()
    user_message = data.get('message')
    story_id = data.get('story_id')
    current_user_id = int(get_jwt_identity())

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if story_id:
        story = Story.query.filter_by(id=story_id, user_id=current_user_id).first()
        if not story:
            return jsonify({"error": "Story not found or access denied"}), 404
    else:
        story = Story(user_id=current_user_id, user_input=json.dumps([]))
        db.session.add(story)
        db.session.commit()

    chat_history = story.get_user_input()
    chat_history.append({"role": "user", "content": user_message})
    ai_response = story_generator.get_follow_up_question(chat_history)

    clean_response = ai_response.strip().upper().replace("\\", "")
    if "READY_TO_GENERATE" in clean_response:
        story.status = 'generating'
        story.set_user_input(chat_history)
        db.session.commit()
        return jsonify({
            "story_id": story.id,
            "response": "Great! I have enough information. I'll start generating your story now.",
            "status": "generating"
        })
    else:
        chat_history.append({"role": "assistant", "content": ai_response})
        story.set_user_input(chat_history)
        db.session.commit()
        return jsonify({
            "story_id": story.id,
            "response": ai_response,
            "status": "gathering_info"
        })

@main_bp.route('/story/<int:story_id>/generate', methods=['GET'])
@jwt_required()
def generate_story_stream(story_id):
    # --- THIS IS THE FIX for the 20-page/duplicate content bug ---
    with story_lock:
        if story_id in generation_locks:
            print(f"STORY {story_id} GENERATION ALREADY IN PROGRESS. SKIPPING DUPLICATE REQUEST.")
            return Response(status=409) # 409 Conflict indicates a duplicate request
        generation_locks[story_id] = True
    # ----------------------------------------------------------------

    def generate():
        try:
            story = Story.query.get_or_404(story_id)
            current_user_id = int(get_jwt_identity())
            if story.user_id != current_user_id:
                yield f"data: {json.dumps({'error': 'Unauthorized'})}\n\n"
                return
            
            if story.pages:
                story.status = 'completed'
                db.session.commit()
                yield f"data: {json.dumps({'status': 'completed'})}\n\n"
                return

            chat_history = story.get_user_input()
            paragraphs = story_generator.generate_story_text(chat_history, story.country_theme)

            if not paragraphs or "Error" in paragraphs[0]:
                story.status = 'failed'
                db.session.commit()
                yield f"data: {json.dumps({'error': 'Failed to generate story text.'})}\n\n"
                return

            if paragraphs and paragraphs[0]:
                story.title = ' '.join(paragraphs[0].split()[:6]) + '...'
                db.session.commit()

            for i, para_text in enumerate(paragraphs[:10]):
                page_no = i + 1
                image_url = story_generator.generate_image_for_paragraph(para_text, story.country_theme)
                new_page = StoryPage(story_id=story.id, page_no=page_no, text=para_text, image_url=image_url)
                db.session.add(new_page)
                db.session.commit()
                data = {"page_no": page_no, "text": para_text, "image_url": image_url}
                yield f"data: {json.dumps(data)}\n\n"
            
            story.status = 'completed'
            story.completed_at = datetime.utcnow()
            db.session.commit()
            yield f"data: {json.dumps({'status': 'completed'})}\n\n"
        finally:
            # --- Unlock the story after generation is done (or if it fails) ---
            with story_lock:
                if story_id in generation_locks:
                    del generation_locks[story_id]
            # -------------------------------------------------------------

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@main_bp.route('/stories', methods=['GET'])
@jwt_required()
def get_user_stories():
    current_user_id = int(get_jwt_identity())
    stories = Story.query.filter_by(user_id=current_user_id).order_by(Story.created_at.desc()).all()
    return jsonify([s.to_dict() for s in stories]), 200

@main_bp.route('/story/<int:story_id>', methods=['GET'])
@jwt_required()
def get_story_details(story_id):
    current_user_id = int(get_jwt_identity())
    story = Story.query.filter_by(id=story_id, user_id=current_user_id).first_or_404()
    return jsonify(story.to_dict(include_pages=True))

@main_bp.route('/story/<int:story_id>/pdf', methods=['GET'])
@jwt_required()
def download_story_pdf(story_id):
    current_user_id = int(get_jwt_identity())
    story = Story.query.filter_by(id=story_id, user_id=current_user_id).first_or_404()
    
    if story.status != 'completed':
        return jsonify({"error": "Story is not complete"}), 400

    pdf_buffer = create_story_pdf(story)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"story_{story.id}.pdf",
        mimetype='application/pdf'
    )
