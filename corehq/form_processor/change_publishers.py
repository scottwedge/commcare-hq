from corehq.apps.change_feed import topics
from corehq.apps.change_feed.producer import producer
from corehq.apps.change_feed import data_sources
from pillowtop.feed.interface import ChangeMeta


def publish_form_saved(form):
    producer.send_change(topics.SQL_FORM, _change_meta_from_sql_form(form))


def _change_meta_from_sql_form(form):
    return ChangeMeta(
        document_id=form.form_id,
        data_source_type=data_sources.FORM_SQL,
        data_source_name='form-sql',  # todo: this isn't really needed.
        document_type='XFormInstanceSQL',  # todo: should this be the same as the couch models?
        document_subtype=form.xmlns,
        domain=form.domain,
        is_deletion=False,
    )
