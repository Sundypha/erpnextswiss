frappe.ui.form.on('Item', {
    refresh(frm) {
        frm.dashboard.add_transactions([
            {
                'label': 'Nonconformity',
                'items': [
                    'Non Conformity Report 8D'
                ]
            }
        ]);
    }
});
