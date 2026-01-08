
import sys
import os

# Ensure root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from body.spine.controller import SpineController

def main():
    print("==========================================")
    print("      THE ECHO (ToneSoul Interface)       ")
    print("==========================================")
    print("Initializing System...")
    
    try:
        spine = SpineController()
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to connect to Spine: {e}")
        return

    print("\nSystem Online. Type 'exit' to quit.")
    print("------------------------------------------")

    while True:
        try:
            user_input = input("\n[USER] > ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                print("Disconnecting...")
                break
                
            response = spine.process_input(user_input)
            
            print(f"\n[TONESOUL] > \n{response}")
            
        except KeyboardInterrupt:
            print("\nDisconnecting...")
            break
        except Exception as e:
            print(f"\n[ERROR] > {e}")

if __name__ == "__main__":
    main()
