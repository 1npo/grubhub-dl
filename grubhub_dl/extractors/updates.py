"""Extracts the data from Grubhub order update email bodies.
"""

# TODO: Find a way to eliminate the need for this helper function, if possible
def reduce_order_update_lists(update_list: list) -> list:
    """Returns the smallest repeating pattern from a list where a sequence of elements is
    repeated 3 times

    This is a helper function needed by ``extract_order_updates`` to get clean data about
    order adjustments, especially in cases where there are multiple items being adjusted
    in the order.

    When iterating through the tables in this type of email body, there are 3 tables
    containing the same adjustment fields. So each field will appear in the field list
    three times. For example, on an order with one updated item and a refund total of
    $3.50, the list for the refund_amount field will contain ['$3.50', '$3.50', '$3.50'].
    
    This function flattens those field lists so that they only contain one instance of
    the field value. Each field needs to be a list instead of a scalar, because multiple
    items can be updated on an order, and we want to capture that detail.
    """

    count = len(update_list) // 3
    items = update_list[:count]
    if update_list[count:2*count] == items and update_list[2*count:] == items:
        return items


def extract_order_update(row: pd.Series) -> pd.Series:
    if row['category'] == 'order_updated':
        soup = BeautifulSoup(row['body'], 'html.parser')

        # TODO: Figure out a better and more reliable way to get the order update details
        items = []
        reasons = []
        item_refunds = []
        for table in soup.find_all('table'):
            for i, table_row in enumerate(table.find_all('td')):
                row_text = table_row.text.strip()
                if row_text == 'Item':
                    items.append(table.find_all('td')[i+1].text.strip())
                if row_text == 'Reason':
                    reasons.append(table.find_all('td')[i+1].text.strip())
                if row_text == 'Refund':
                    item_refunds.append(table.find_all('td')[i+1].text.strip())
                if row_text == 'Fees & taxes':
                    row['refund_fees_amount'] = table.find_all('td')[i+1].text.strip()
                if row_text == 'Adjusted tip':
                    row['tip_adjusted_amount'] = table.find_all('td')[i+1].text.strip()
                if row_text in ('Refund total', 'Total refund'):
                    row['refund_amount'] = table.find_all('td')[i+1].text.strip()
                if 'Regarding order' in row_text:
                    row['order_number'] = row_text.split('Regarding order ')[1].strip()
        
        # file_name = Path(row['file_path']).name
        # logger.debug('')
        # logger.debug('%s', '=' * (len(file_name) + 10))
        # logger.debug('DEBUG FOR %s', file_name)
        # logger.debug('%s', '=' * (len(file_name) + 10))
        # logger.debug('ITEMS                   = %s', items)
        # logger.debug('ITEMS -- REDUCED        = %s', reduce_order_update_lists(items))
        # logger.debug('%s', '-' * (len(file_name) + 10))
        # logger.debug('REASONS                 = %s', reasons)
        # logger.debug('REASONS -- REDUCED      = %s', reduce_order_update_lists(reasons))
        # logger.debug('%s', '-' * (len(file_name) + 10))
        # logger.debug('ITEM REFUNDS            = %s', item_refunds)
        # logger.debug('ITEM REFUNDS -- REDUCED = %s', reduce_order_update_lists(item_refunds))
        # logger.debug('')
        # row['refund_item'] = reduce_order_update_lists(items)
        # row['refund_reason'] = reduce_order_update_lists(reasons)
        # row['refund_item_amount'] = reduce_order_update_lists(item_refunds)
    return row
