import traceback
import sys

try:
    import r2r
except Exception as e:
    print("Error details:", file=sys.stderr)
    traceback.print_exc()
