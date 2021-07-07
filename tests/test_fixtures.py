import os
import pytest
from agavepy.agave import Agave
from reactors.runtime import Reactor


@pytest.mark.tapis_auth
class TestAuthFixtures:
    
    def test_client_v2(self, client_v2):
        """Test fixture `client_v2`"""
        assert isinstance(client_v2, Agave)
        _ = client_v2.apps.list()


    def test_token_v2(self, token_v2):
        """Test fixture `token_v2`"""
        assert isinstance(token_v2, str)
        assert token_v2


    def test_abaco_username(self, abaco_username):
        """Test fixture `abaco_username`"""
        assert abaco_username is None
        assert '_abaco_username' in os.environ


    def test_abaco_api_server(self, abaco_api_server):
        """Test fixture `abaco_api_server`"""
        assert abaco_api_server is None
        assert '_abaco_api_server' in os.environ


    def test_abaco_access_token(self, abaco_access_token):
        """Test fixture `abaco_access_token`"""
        assert abaco_access_token is None
        assert '_abaco_access_token' in os.environ


@pytest.mark.tapis_auth
class TestReactorFixtures:

    def test_r(self, r):
        """Test fixture `r`"""
        assert isinstance(r, Reactor)
        # check that client is active
        _ = r.client.apps.list()


@pytest.mark.tapis_auth
class TestLiveFixtures:
    """Test fixtures that provide Tapis entities (apps, actors, files, etc.)
    for integration testing.
    """

    def test_actor_wc(self, actor_wc):
        """Test fixture `actor_wc`"""
        pass
