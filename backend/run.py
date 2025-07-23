from app import create_app
import os

app = create_app()

if __name__ == '_main_':
    # Only run in debug mode in development
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)