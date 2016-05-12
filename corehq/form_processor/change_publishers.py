from corehq.apps.change_feed import topics
from corehq.apps.change_feed.producer import producer
from corehq.apps.change_feed import data_sources
from corehq.form_processor.signals import sql_case_post_save
from pillowtop.feed.interface import ChangeMeta


def publish_form_saved(form):
    producer.send_change(topics.FORM_SQL, change_meta_from_sql_form(form))


def change_meta_from_sql_form(form):
    return ChangeMeta(
        document_id=form.form_id,
        data_source_type=data_sources.FORM_SQL,
        data_source_name='form-sql',  # todo: this isn't really needed.
        document_type=form.state,
        document_subtype=form.xmlns,
        domain=form.domain,
        is_deletion=False,
    )


def publish_case_saved(case, send_post_save_signal=True):
    """
    Publish the change to kafka and run case post-save signals.
    """
    producer.send_change(topics.CASE_SQL, change_meta_from_sql_case(case))
    if send_post_save_signal:
        sql_case_post_save.send(case.__class__, case=case)


def change_meta_from_sql_case(case):
    return ChangeMeta(
        document_id=case.case_id,
        data_source_type=data_sources.CASE_SQL,
        data_source_name='case-sql',  # todo: this isn't really needed.
        document_type='CommCareCaseSql',  # todo: should this be the same as the couch models?
        document_subtype=case.type,
        domain=case.domain,
        is_deletion=False,
    )


def publish_case_deleted(domain, case_id):
    producer.send_change(topics.CASE_SQL, ChangeMeta(
        document_id=case_id,
        data_source_type=data_sources.CASE_SQL,
        data_source_name='case-sql',  # todo: this isn't really needed.
        document_type='CommCareCaseSql',  # todo: should this be the same as the couch models?
        document_subtype=None,  # todo: does this need a value?
        domain=domain,
        is_deletion=True,
    ))


def publish_ledger_v2_saved(ledger_value):
    producer.send_change(topics.LEDGER, change_meta_from_ledger_v2(ledger_value))


def change_meta_from_ledger_v2(ledger_value):
    return ChangeMeta(
        document_id=ledger_value.ledger_reference.as_id(),
        data_source_type=data_sources.LEDGER_V2,
        data_source_name='ledger-v2',  # todo: this isn't really needed.
        domain=ledger_value.domain,
        is_deletion=False,
    )


def publish_stock_state_saved(stock_state):
    producer.send_change(topics.LEDGER, change_meta_from_stock_state(stock_state))


def change_meta_from_stock_state(stock_state):
    return ChangeMeta(
        document_id=stock_state.pk,
        data_source_type=data_sources.LEDGER_OLD,
        data_source_name='ledger',  # todo: this isn't really needed.
        domain=stock_state.domain,
        is_deletion=False,
    )
