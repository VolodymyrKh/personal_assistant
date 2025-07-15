from src.models import CustomValueError, PhoneValidationError


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
        except PhoneValidationError:
            return "Phone nr is not valid, please use 10 digits to specify one."
        except CustomValueError as e:
            return str(e).strip()
    return inner