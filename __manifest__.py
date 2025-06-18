# -*- coding: utf-8 -*-
{
    'name': 'Sistemas de comisiones',
    'version': '1.0',
    'description': 'Agrega comisiones en las ventas',
    'summary': 'Agrega comisiones en las ventas',
    'author': 'DGV',
    'website': 'https://github.com/AlfaSystemas5457/commissions',
    'license': 'LGPL-3',
    'category': 'Other Category',
    'depends': [
        'stock',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/manu_view.xml',
        'views/commissions_view.xml',
        'views/plans_view.xml',
    ],
    'auto_install': False,
    'application': True,
    'sequence': 0,
}
