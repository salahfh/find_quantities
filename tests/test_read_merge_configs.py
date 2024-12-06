from find_quantity.read_merge_configs import PackageDefinitionsConstructor, MergeRule

def test_merge_product_names_with_i_o_n_article():
    package_names = ['AS-12UW4SGETU00-I', 'AS-12UW4SGETU00-O', 'OTHER']

    pdc = PackageDefinitionsConstructor(merge_rules=[])
    package_definitions = pdc.merge_int_i_and_ext_o_rule(product_n_articles=package_names)
    
    assert len(package_definitions) == 1
    assert sorted(package_definitions[0]) == ['AS-12UW4SGETU00-I', 'AS-12UW4SGETU00-O']


def test_merge_product_names_with_i_o_n_article_with_multiple_products():
    package_names = ['AS-12UW4SGETU00-I',
                     'AS-12UW4SGETU00-O',
                     'OTHER',
                     'CMS542-A6IT3-O',
                     'CMS542-A6IT3-I',
                     ]

    pdc = PackageDefinitionsConstructor(merge_rules=[])
    package_definitions = pdc.merge_int_i_and_ext_o_rule(product_n_articles=package_names)
    assert len(package_definitions) == 2

def test_merged_product_names_with_pattern():
    package_names = [
        'NCE185',
        'NCE185CMD',
        'NCE150',
        'NCE150CMD',
        'KCG406',
    ]

    pdc = PackageDefinitionsConstructor(merge_rules=[])
    package_definitions = pdc.merge_based_on_pattern(product_n_articles=package_names, pattern=r"^NCE\d{3}")
    
    assert len(package_definitions) == 2


def test_merge_products_defined_in_custom_list():
    package_names = [
        'NCE185',
        'NCE150',
        'KCG406',
    ]

    pdc = PackageDefinitionsConstructor(merge_rules=[])
    package_definitions = pdc.merge_products_from_predefine_list(product_n_articles=package_names)
    
    assert len(package_definitions) == 1


def test_package_definitions_constructor_with_mixed_rules():
    merge_rules = [
        MergeRule('', 'AutoMergeIOProducts'),
        MergeRule('', 'AutoMergeNCEProducts'),
        MergeRule('', 'CombineProducts', ['CMD211', 'CRG14CL1N', 'CRG14CL1NCMD']),
    ]
    package_names = [
        'NCE185',
        'NCE185CMD',
        'NCE150',
        'NCE150CMD',
        'KCG406',
        'OTHER',
        'CMS542-A6IT3-O',
        'CMS542-A6IT3-I',
    ]

    pkgs = PackageDefinitionsConstructor(merge_rules=merge_rules).make_package_definitions(package_names)
    print(pkgs)
    assert len(pkgs) == 12