from django.core.management.commands.runserver import Command as RunserverCommand

class Command(RunserverCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        # Set default host and port
        parser.set_defaults(addrport='127.0.0.1:8080')
