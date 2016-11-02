import pytest

from solc import compile_files


from populus.migrations.migration import (
    get_migration_classes_for_execution,
)
from populus.project import Project
from populus.compilation import find_project_contracts
from populus.utils.filesystem import recursive_find_files


CACHE_KEY_MTIME = "populus/project/compiled_contracts_mtime"
CACHE_KEY_CONTRACTS = "populus/project/compiled_contracts"


@pytest.fixture(scope="session")
def project(request):
    # This should probably be configurable using the `request` fixture but it's
    # unclear what needs to be configurable.

    # use pytest cache to preset the sessions project to recently compiled contracts
    contracts = request.config.cache.get(CACHE_KEY_CONTRACTS, None)
    mtime = request.config.cache.get(CACHE_KEY_MTIME, None)
    project = Project()


    base_tests_dir = os.path.dirname(__file__)

    solidity_source_files = recursive_find_files(base_tests_dir, 'Test*.sol')
    compiled_contracts = compile_files(solidity_source_files)
    for contract_name, contract_data in compiled_contracts.items():
        project.compiled_contracts.setdefault(contract_name, contract_data)

    return project

    project.fill_contracts_cache(contracts, mtime)
    request.config.cache.set(CACHE_KEY_CONTRACTS, project.compiled_contracts)
    request.config.cache.set(CACHE_KEY_MTIME, project.get_source_modification_time())

    return project


@pytest.fixture(scope="session", autouse=True)
def test_contracts(project):
    base_tests_dir = os.path.join(project.project_dir, 'tests')

    test_source_files = [
        os.path.relpath(source_path, project.project_dir)
        for source_path in recursive_find_files(base_tests_dir, 'Test*.sol')
    ]
    all_source_files = test_source_files + list(find_project_contracts(
        project.project_dir, project.contracts_dir,
    ))
    compiled_contracts = compile_files(all_source_files)
    for contract_name, contract_data in compiled_contracts.items():
        project.compiled_contracts.setdefault(contract_name, contract_data)


@pytest.yield_fixture()
def unmigrated_chain(request, project):
    # This should probably allow you to specify the test chain to be used based
    # on the `request` object.  It's unclear what the best way to do this is
    # so... punt!
    chain = project.get_chain('testrpc')

    # TODO: this should run migrations.  If `testrpc` it should be snapshotted.
    # In the future we should be able to snapshot the `geth` chains too and
    # save them for faster test runs.

    with chain:
        yield chain


@pytest.fixture()
def chain(unmigrated_chain):
    # Determine if we have any migrations to run.
    migrations_to_execute = get_migration_classes_for_execution(
        unmigrated_chain.project.migrations,
        unmigrated_chain,
    )

    for migration in migrations_to_execute:
        migration.execute()

    return unmigrated_chain


@pytest.fixture()
def web3(unmigrated_chain):
    return unmigrated_chain.web3


@pytest.fixture()
def contracts(unmigrated_chain):
    return unmigrated_chain.contract_factories


@pytest.fixture()
def accounts(web3):
    return web3.eth.accounts
