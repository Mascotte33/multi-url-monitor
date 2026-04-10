import requests

from worker import log_level, check_url
from unittest.mock import MagicMock

def test_log_level():
    assert log_level({'status': 200, 'duration': 0, 'error': None}) == 'INFO'
    assert log_level({'status': 200, 'duration': 2, 'error': None}) == 'WARNING'
    assert log_level({'status': 300, 'duration': None, 'error': 'Exception'}) == 'ERROR'
    assert log_level({'status': None, 'duration': None, 'error': 'Exception'}) == 'ERROR'

def test_check_url_success(mocker):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mocker.patch('worker.requests.get', return_value=mock_response)
    result = check_url('http://fake-url.com')
    assert result['status'] == 200
    assert result['error'] is None


def test_check_url_timeout(mocker):
    mock_response = MagicMock()
    mock_response.status_code = 408
    mocker.patch('worker.requests.get', side_effect=requests.exceptions.Timeout)
    result = check_url('http://fake-url.com')
    assert result['status'] == None
    assert result['error'] == 'Timeout Exception'

def test_check_url_error(mocker):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mocker.patch('worker.requests.get', side_effect=requests.exceptions.ConnectionError)
    result = check_url('http://fake-url.com')
    assert result['status'] == None
    assert result['error'] == 'Connection Exception'


