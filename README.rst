====================
Adding post to queue
====================

Queue
^^^^^

scheduler_queue

Arguments
^^^^^^^^^

**action**
  *add*

**delay_time** or **trigger_time** (int)
  when event will be fired (in seconds since epoch)

**data** (dict)
  data that will be sent to poster queue when event is triggered

  If data['posts'] is array and its members has "lt_post_id" key, then scheduler will try to set event_id field for posts with id=lt_post_id

Example
^^^^^^^

 {"action": "add",  "lt_post_id": 1, "delay_time": 129, "data": {"action": "add", "message": "You are welcome", "access_token": 'adqw'}}

 
 # ./amqp.py scheduler_queue action=add delay_time=6 lt_post_id=1 data="{'action': 'add', 'message': 'You are welcome', 'access_token': 'adqw'}"

========================
Deleting post from queue
========================

Queue
^^^^^
scheduler_queue

Arguments
^^^^^^^^^

**action**
  *delete*

**event_id** (int)
  id of event to be deleted

Example
^^^^^^^
 {"action": "delete", "event_id": 1}

 # ./amqp.py scheduler_queue action=delete event_id=1

=======================
Updating event in queue
=======================

Queue
^^^^^

scheduler_queue

Arguments
^^^^^^^^^

**action**
  *update*

**event_id**
  id of event to be updated

**new_trigger_time**
  integer
  
**new_data**
  new data that will be sent to poster queue when event is triggered

Example
^^^^^^^

 {"action": "update", "event_id": 1, "new_delay_time": 129, "new_data": {"action": "add", "message": "You are welcome"}}
    
 # ./amqp.py scheduler_queue action=update event_id=1 new_delay_time=129 new_data="{'action': 'add', 'message': 'You are welcome'}"


==========================
Marking event as processed
==========================

Queue
^^^^^

scheduler_queue

Arguments
^^^^^^^^^

**action**
  *mark_as_processed*

**event_id**
  id of event to be marked as processed

Example
^^^^^^^

 {"action": "mark_as_processed", "event_id": 1}
    
 # ./amqp.py scheduler_queue action=mark_as_processed event_id=1

=================
Adding post to VK
=================

Queue
^^^^^

posting_queue

Arguments
^^^^^^^^^

**event_id**
  id of event associated with the post. when post will be added, poster'll send message to mark it as processed

**action** (string)
  *add*

**event_id**
  id of event associated with this post

**lt_post_id**
  id of post in DB for which will be 

**attachments**
  post attachments

**text** (string)
  text of post

**owner_ids** (int or array)
  one ID of wall owner or array of wall ID where it will be posted

**from_group** (boolean)
  should post be added on behalf of group?

**attachments** (string)
  list of attachable media for post (eg., photo or video)

**access_token**
  token for accessing VK API

Example
^^^^^^^
    
===================
Delete post from VK
===================

Queue
^^^^^
posting_queue

Arguments
^^^^^^^^^


**event_id**
  id of event associated with the post. when post will be deleted, poster'll send message to mark it as processed

**action** (string)
  *delete*

**lt_post_id** (int)
  if the parameter is passed, then both owner_id and post_id are read from DB (post with id == lt_post_id)

**post_id** (int)
  internal post id within vk

**owner_id** (int)
  internal owner id within vk

**access_token**
  token for accessing VK API
