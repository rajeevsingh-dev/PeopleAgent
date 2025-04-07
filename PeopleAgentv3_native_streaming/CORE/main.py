import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

# Add parent directory to sys.path so Python can find the packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables from .env file
load_dotenv()

# Set up basic logging until full configuration is loaded
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

try:
    from PeopleAgentv2.UTIL.config import load_config
    from PeopleAgentv2.UTIL.logging_setup import setup_logging
    from PeopleAgentv2.CORE.people_agent import PeopleAgent
except ImportError as e:
    logger.error(f"Import error: {e}")
    print(f"Import error: {e}")
    sys.exit(1)

async def main():
    """
    Entry point with user interaction in a loop.
    """
    try:
        # Configure logging from environment variables
        try:
            log_level = os.getenv('LOG_LEVEL', 'INFO')
            log_file = os.getenv('LOG_FILE', 'people_agent.log')  # This is where the log file is defined
            log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            log_config = {
                'level': log_level,
                'file': log_file,
                'format': log_format
            }
            
            # Set up logging with environment variables
            logger = setup_logging(log_config)
            logger.info("Logging configured from environment variables")
        except Exception as e:
            print(f"Warning: Could not fully configure logging: {e}")
            logger.warning(f"Could not fully configure logging: {e}")
        
        # Load config for other settings
        try:
            config = load_config()
            logger.info("Configuration loaded")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            print(f"Error loading configuration: {e}")
            return 1

        print("USERS MUST ENTER A SPECIFIC USER IDENTIFIER (email, ID, or name) FOR APP-ONLY QUERIES.\n")
        target_user = input("Enter the user's email, Azure AD object ID, or name (leave blank to get all users): ")
        logger.debug(f"User input: {target_user}")

        # Handle no user input (show all)
        if not target_user:
            logger.info("No target user specified, showing all users")
            agent = PeopleAgent("")
        else:
            # If input doesn't look like email or GUID, try name search
            if "@" not in target_user and len(target_user) != 36:
                logger.info(f"Searching for user by name: {target_user}")
                temp_agent = PeopleAgent("")  # for searching
                print("\nSearching users by name...")
                search_results = await temp_agent.find_user_by_name(target_user)
                if isinstance(search_results, str):
                    error_msg = f"Error: {search_results}"
                    logger.error(error_msg)
                    print(f"\n{error_msg}")
                    return 1
                
                matches = search_results.get("value", [])
                if not matches:
                    logger.info("No users found with that name.")
                    print("\nNo users found with that name.")
                    return 1

                if len(matches) > 1:
                    logger.info("Multiple users found.")
                    print("\nMultiple users found:")
                    for i, user in enumerate(matches, 1):
                        print(f"{i}. {user.get('displayName')} ({user.get('mail')})")
                    choice = input("\nEnter the number of the user you want to inspect (or 0 to exit): ")
                    if not choice.isdigit() or int(choice) == 0:
                        logger.info("Exiting due to user choice.")
                        print("\nExiting...")
                        return 0
                    if int(choice) < 1 or int(choice) > len(matches):
                        logger.info("Invalid choice by user.")
                        print("\nInvalid choice. Exiting...")
                        return 1
                    target_user = matches[int(choice)-1].get('mail')
                else:
                    target_user = matches[0].get('mail')
                    logger.info(f"Found user: {matches[0].get('displayName')} ({target_user})")
                    print(f"\nFound user: {matches[0].get('displayName')} ({target_user})")

            agent = PeopleAgent(target_user)

        print("\nWelcome to the Microsoft 365 People Agent!")
        print("You can ask about a person's profile, manager, devices, or switch to another user.")
        print("Type 'exit' to quit.\n")

        while True:
            try:
                if not agent.user_identifier.strip():
                    logger.info("Fetching all users (app-only mode).")
                    print("\nFetching all users (app-only mode)...")
                    all_users_raw = await agent.get_all_users()
                    all_users_formatted = agent.format_data("all_users", all_users_raw)
                    print("\nAll Users:", all_users_formatted)
                    print('\n(Enter a valid user ID/email/name to inspect a particular user, or type "exit")')
                    new_identifier = input("\nUser ID/Email/Name to inspect? ").strip()
                    if new_identifier.lower() == "exit":
                        logger.info("Gracefully shutting down due to user input.")
                        print("\nGracefully shutting down...")
                        break

                    if "@" not in new_identifier and len(new_identifier) != 36:
                        logger.info(f"Searching for user by name: {new_identifier}")
                        print("\nSearching users by name...")
                        search_results = await agent.find_user_by_name(new_identifier)
                        matches = search_results.get("value", [])
                        if matches:
                            if len(matches) > 1:
                                print("\nMultiple users found:")
                                for i, user in enumerate(matches, 1):
                                    print(f"{i}. {user.get('displayName')} ({user.get('mail')})")
                                choice = input("\nEnter the number of the user you want to inspect (or 0 to exit): ")
                                if not choice.isdigit() or int(choice) == 0:
                                    continue
                                if int(choice) < 1 or int(choice) > len(matches):
                                    print("\nInvalid choice.")
                                    continue
                                new_identifier = matches[int(choice)-1].get('mail')
                            else:
                                new_identifier = matches[0].get('mail')
                                print(f"\nFound user: {matches[0].get('displayName')} ({new_identifier})")
                        else:
                            print("\nNo users found with that name.")
                            continue

                    agent = PeopleAgent(new_identifier)
                    continue

                prompt_msg = (
                    "\nAsk a question about this user, "
                    "enter another user's email/ID/name to switch, "
                    "or type 'exit' to quit:\n"
                )
                user_input = input(prompt_msg).strip()

                if user_input.lower() == 'exit':
                    logger.info("Gracefully shutting down due to user input.")
                    print("\nGracefully shutting down...")
                    break

                # If input might be a user identifier, try switching users
                if "@" in user_input or len(user_input) == 36 or (
                    user_input and not user_input.lower().startswith(("what", "who"))
                ):
                    if "@" not in user_input and len(user_input) != 36:
                        logger.info(f"Searching for user by name: {user_input}")
                        print("\nSearching users by name...")
                        search_results = await agent.find_user_by_name(user_input)
                        matches = search_results.get("value", [])
                        
                        if matches:
                            if len(matches) > 1:
                                print("\nMultiple users found:")
                                for i, user in enumerate(matches, 1):
                                    print(f"{i}. {user.get('displayName')} ({user.get('mail')})")
                                choice = input("\nEnter the number of the user you want to inspect (or 0 to cancel): ")
                                if not choice.isdigit() or int(choice) == 0:
                                    continue
                                if int(choice) < 1 or int(choice) > len(matches):
                                    print("\nInvalid choice.")
                                    continue
                                user_input = matches[int(choice)-1].get('mail')
                            else:
                                user_input = matches[0].get('mail')
                                print(f"\nFound user: {matches[0].get('displayName')} ({user_input})")
                        else:
                            print("\nNo users found with that name. Treating as a question.")
                            print("\nProcessing your query...")
                            response = await agent.process_query(user_input)
                            print("\nResponse:", response)
                            continue

                    print(f"\nSwitching to user: {user_input}")
                    agent = PeopleAgent(user_input)
                    continue

                print("\nProcessing your query...")
                response = await agent.process_query(user_input)
                print("\nResponse:", response)

            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt. Shutting down gracefully.")
                print("\n\nReceived keyboard interrupt. Shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                print(f"\nError processing query: {str(e)}")
                print("Please try again or type 'exit' to quit.")

    except KeyboardInterrupt:
        logger.info("Shutdown requested. Exiting.")
        print("\n\nShutdown requested. Exiting...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\nFatal error: {str(e)}")
        return 1
    finally:
        logger.info("Thank you for using the People Agent!")
        print("\nThank you for using the People Agent!")
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Program terminated by user.")
        print("\n\nProgram terminated by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)