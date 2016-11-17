import pytest


def test_contract_factory_availability_with_no_dependencies(chain,
                                                            math):
    provider = chain.store.provider

    is_available = provider.are_contract_factory_dependencies_available('Math')
    assert is_available is True


def test_contract_factory_availability_with_missing_dependency(chain,
                                                               multiply_13):
    provider = chain.store.provider

    is_available = provider.are_contract_factory_dependencies_available('Multiply13')
    assert is_available is False


def test_contract_factory_availability_with_bytecode_mismatch_on_dependency(chain,
                                                                            multiply_13,
                                                                            math):
    provider = chain.store.provider
    registrar = chain.store.registrar

    registrar.set_contract_address('Library13', math.address)

    is_available = provider.are_contract_factory_dependencies_available('Multiply13')
    assert is_available is False


def test_contract_factory_availability_with_dependency(chain,
                                                       multiply_13,
                                                       library_13):
    provider = chain.store.provider
    registrar = chain.store.registrar

    registrar.set_contract_address('Library13', library_13.address)

    is_available = provider.are_contract_factory_dependencies_available('Multiply13')
    assert is_available is True
