import os
import sys

if __name__ == "__main__":
    # Ensure src directory is in sys.path for absolute imports
    sys.path.insert(0, os.path.dirname(__file__))
    from engine import main

    main()
