import os
import pytest
from tscraper.tscraper import load_yaml_config, ConfigError

def test_load_yaml_config_invalid_structure(tmp_path):
    config_path = tmp_path / 'config.yaml'
    config_path.write_text("invalid: true")
    os.environ['CONFIG_PATH'] = str(config_path)
    with pytest.raises(ConfigError, match="Missing target_channels in config"):
        load_yaml_config()

def test_load_yaml_config_empty(tmp_path):
    config_path = tmp_path / 'config.yaml'
    config_path.write_text("")
    os.environ['CONFIG_PATH'] = str(config_path)
    with pytest.raises(ConfigError, match="Invalid config structure"):
        load_yaml_config()

def test_load_yaml_config_valid(tmp_path):
    config_path = tmp_path / 'config.yaml'
    config_path.write_text("""
channels:
    news_ai:
        - "@channel1"
    target_channels:
        news_ai: "@target"
    """)
    os.environ['CONFIG_PATH'] = str(config_path)
    config = load_yaml_config()
    assert 'news_ai' in config['channels']
    assert config['channels']['target_channels']['news_ai'] == '@target'
