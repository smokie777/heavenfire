from datetime import datetime
from helpers import obfuscate_prompt_username
from InstanceContainer import InstanceContainer

PAGINATION_ROW_COUNT = 25

class Message(InstanceContainer.db.Model):
  """Keeps track of all messages generated by Luna on Twitch."""

  id = InstanceContainer.db.Column(
    InstanceContainer.db.Integer,
    primary_key=True,
    autoincrement=True
  )
  created_at = InstanceContainer.db.Column(
    InstanceContainer.db.DateTime,
    nullable=False,
    default=datetime.now
  )
  prompt = InstanceContainer.db.Column(
    InstanceContainer.db.Text,
    nullable=False
  )
  response = InstanceContainer.db.Column(
    InstanceContainer.db.Text,
    nullable=False
  )
  latency_llm = InstanceContainer.db.Column(
    InstanceContainer.db.Float,
    nullable=False,
  )
  latency_tts = InstanceContainer.db.Column(
    InstanceContainer.db.Float,
    nullable=False,
  )
class MessageSchema(InstanceContainer.ma.SQLAlchemySchema):
  class Meta:
    model = Message
  id=InstanceContainer.ma.auto_field()
  created_at=InstanceContainer.ma.auto_field()
  prompt=InstanceContainer.ma.auto_field()
  response=InstanceContainer.ma.auto_field()
  latency_llm=InstanceContainer.ma.auto_field()
  latency_tts=InstanceContainer.ma.auto_field()
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)
def db_message_get_by_page(page):
  rows = Message.query \
    .order_by(Message.created_at.desc()) \
    .offset((page - 1) * PAGINATION_ROW_COUNT) \
    .limit(PAGINATION_ROW_COUNT) \
    .all()
  return messages_schema.dump(rows)
def db_message_insert_one(prompt, response, latency_llm, latency_tts):
  row = Message(
    prompt=obfuscate_prompt_username(prompt),
    response=response,
    latency_llm=latency_llm,
    latency_tts=latency_tts
  )
  InstanceContainer.db.session.add(row)
  InstanceContainer.db.session.commit()
def db_message_get_last_five():
  rows = Message.query.order_by(Message.created_at.desc()).limit(5).all()
  return messages_schema.dump(rows)

class Event(InstanceContainer.db.Model):
  """Keeps track of twitch event usage, such as channel point redemptions & chat commands."""

  id = InstanceContainer.db.Column(
    InstanceContainer.db.Integer,
    primary_key=True,
    autoincrement=True
  )
  created_at = InstanceContainer.db.Column(
    InstanceContainer.db.DateTime,
    nullable=False,
    default=datetime.now
  )
  type = InstanceContainer.db.Column(
    InstanceContainer.db.Text, # should ideally be enum based on TWITCH_EVENT_TYPE
    nullable=False
  )
  event = InstanceContainer.db.Column(
    InstanceContainer.db.Text,
    nullable=False
  )
  body = InstanceContainer.db.Column(
    InstanceContainer.db.Text,
    nullable=True
  )
class EventSchema(InstanceContainer.ma.SQLAlchemySchema):
  class Meta:
    model = Event
  id=InstanceContainer.ma.auto_field()
  created_at=InstanceContainer.ma.auto_field()
  type=InstanceContainer.ma.auto_field()
  event=InstanceContainer.ma.auto_field()
  body=InstanceContainer.ma.auto_field()
event_schema = EventSchema()
events_schema = EventSchema(many=True)
def db_event_get_by_page(page):
  rows = Event.query \
    .order_by(Event.created_at.desc()) \
    .offset((page - 1) * PAGINATION_ROW_COUNT) \
    .limit(PAGINATION_ROW_COUNT) \
    .all()
  return events_schema.dump(rows)
def db_event_insert_one(type, event, body = None):
  row = Event(
    type=type,
    event=event,
    body=body
  )
  InstanceContainer.db.session.add(row)
  InstanceContainer.db.session.commit()

# create database
with InstanceContainer.app.app_context():
  InstanceContainer.db.create_all()
