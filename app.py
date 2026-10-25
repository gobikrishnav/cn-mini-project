"""
NetLab-Pro: Master Python Entry Point
Usage:
    python app.py          # Launches Web Application in Chrome / Default Browser
    python app.py --gui    # Launches Native Desktop GUI
    python app.py --cli    # Launches Terminal Interactive CLI
"""

import sys

if __name__ == "__main__":
    if "--gui" in sys.argv:
        import gui_app
        gui_app.main()
    elif "--cli" in sys.argv:
        import interactive_cli
        interactive_cli.main()
    else:
        import threading
        import server
        threading.Timer(1.2, server.launch_browser).start()
        server.app.run(host="0.0.0.0", port=5000, debug=False)
