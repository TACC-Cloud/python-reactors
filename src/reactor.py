from reactors.runtime import Reactor

def main():
    """Main usage text for this Reactors container image
    """
    # Tapis is set to optional so that first-time users won't be 
    # scared off with a Tapis authorization error because they did 
    # not pass in proper credentials
    r = Reactor(tapis_optional=True)
    # TODO - Improve this to make tacc/reactors:python3 show basic usage info
    r.logger.info("Hello from {0}".format(__file__))
    r.on_success("Execution complete")

if __name__ == '__main__':
    main()
