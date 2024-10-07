from ruamel.yaml import YAML
import json

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.preserve_quotes = True
yaml.width = 4096  # Set a large line width to prevent wrapping


def load_json_variables(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def format_commands(commands):
    from ruamel.yaml.scalarstring import LiteralScalarString
    return LiteralScalarString('\n'.join(commands) + '\n')


def format_plugins(plugins):
    formatted_plugins = []
    for plugin in plugins:
        name = list(plugin.keys())[0]
        properties = plugin[name]
        formatted_plugin = {name: {
            k: v for k, v in properties.items()
        }}
        formatted_plugins.append(formatted_plugin)
    return formatted_plugins


def generate_yaml_data(items):
    steps = []
    for item in items:
        step_cache_folder = f"/var/cache/buildkite/{item['key']}"
        if item.get('depends_on'):
            step = {
                'label': item['label'],
                'key': item['key'],
                'depends_on': item['depends_on'],
                'commands': format_commands(item['commands']),
                'plugins': format_plugins(item['plugins'])
            }
            if 'clone' in item['key']:
                step["env"] = {
                    "BUILDKITE_PLUGIN_FS_CACHE_FOLDER": step_cache_folder
                }
        else:
            step = {
                'label': item['label'],
                'key': item['key'],
                'commands': format_commands(item['commands']),
                'plugins': format_plugins(item['plugins'])
            }
            if 'clone' in item['key']:
                step["env"] = {
                    "BUILDKITE_PLUGIN_FS_CACHE_FOLDER": step_cache_folder
                }
        steps.append(step)

    # Generate env dictionary, too
    env = {
        'AWS_REGION': 'eu-west-1',
        'AWS_ACCOUNT_ID': '1234567890',
        'ECR_REPOSITORY': 'polar-bookstore',
        'VERSION': 'Buildkite-v1'
    }

    # and don't forget our queue specification
    agents = {
        'queue': 'new_queu'
    }

    return {'agents': agents, 'env': env, 'steps': steps}


def save_yaml(data, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(data, file)


def main():
    variables_path = '.buildkite/variables.json'
    output_path = '.buildkite/pipeline.yml'
    items = load_json_variables(variables_path)
    yaml_data = generate_yaml_data(items)
    save_yaml(yaml_data, output_path)
    print(f"YAML file generated and saved to {output_path}")


if __name__ == "__main__":
    main()
