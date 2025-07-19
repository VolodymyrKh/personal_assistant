from src.models import CustomValueError, PhoneValidationError, EmailValidationError, BirthdayValidationError


def input_error(fn):
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        
        except ValueError:
            return "Please enter valid arguments for the command."
        except IndexError:
            return "Please enter the argument for the command"
        except KeyError:
            return "Contact is not in the list. Use 'add' command to create one."
        except PhoneValidationError as e:
            return f"Phone validation error: {str(e)}"
        except EmailValidationError as e:
            return f"Email validation error: {str(e)}"
        except BirthdayValidationError as e:
            return f"Birthday validation error: {str(e)}"
        except CustomValueError as e:
            return str(e).strip()
    return inner