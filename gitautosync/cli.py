import click


@click.command()
@click.option('--as-cowboy', '-c', is_flag=True, help='Greet as a cowboy.')
@click.argument('name', default='world', required=False)
def main(name, as_cowboy):
    """Synchronizes a github repository with a local repository. Automatically deals with conflicts and produces useful output to stdout."""
    greet = 'Howdy' if as_cowboy else 'Hello'
    click.echo('{0}, {1}.'.format(greet, name))
