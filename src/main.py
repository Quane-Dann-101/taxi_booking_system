import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from login_window import LoginWindow

def main():
    # Set WebEngine flags before creating QApplication
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
