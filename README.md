# NextDoor, an app for the locals of Brooklyn

A full-stack web application that provides an online service that allows people to communicate with others in their neighborhood. They can then send and receive messages to other users living close by, and participate in discussions with those users.

# Features developed:
## User sign up and profile creation:
  Users will be able to register for the service and specify where they live; this is done by providing an address. They can post a short profile where they introduce themselves and maybe their family, including optionally a photo. They have the option to update and modify their profiles

## Joining groups:
In the website, there are two levels of locality, hoods (neighborhoods, such as Bay Ridge or Park Slope) and blocks (a part of a neighborhood but not necessarily one block, e.g., “7th Avenue between 3rd and 6th Street in Park Slope”). Each block belongs to exactly one neighborhood. Users can apply to join a block; they are accepted as a new member if at least three existing members (or all members if there are less than three) approve. A user can only be member of one block, and is also automatically a member of the neighborhood in which the block is located. Users can also choose to follow other blocks, which means they can read messages sent to that block or to the hood in which that block is, but they cannot post and they are not members. Users who move may leave one block and/or hood and apply for membership in another block.

## Adding friends and neighbors:
Members can specify two types of relationships with other members. They can friend other members, including members not in the same hood or block, and they can specify (direct) neighbors, i.e., members of the same block that live next door, in the same building, or very close by. Friendship is symmetric and requires both sides to accept, while neighbors can be chosen unilaterally. Also, people should be able to post, read, and reply to messages.

## Content posting:
Users can start a new topic by choosing a subject, and also chooses who can read the message and reply to it. A user can direct a message to a particular person who is a friend or a neighbor, or all of their friends or all of their neighbors, or to the entire block or the entire hood they are a member of. When others reply to a message, their reply can be read and replied to by anyone who received the earlier message. Thus, messages are organized into threads, where each thread is started by an initial message and is visible by the group of people specified in the initial message. A message consists of a title and a set of recipients (specified in the inital message), an author, a timestamp, a text body, and optionally the coordinates of a location the message refers to.

## User feed:
The user's feed is separated into neighbor feeds, friend feeds, block feeds, and hood feeds to view repective threads from each of them. The website store information about past accesses to the site by
each user, so that the system can optionally show only threads with new messages posted since the last time the user visited the site, or profiles of new members, or threads with messages that are still unread.

## Browse and search messages:
Users can search for messages with a certain keyword that is present in any of their feeds. It list all threads in a user’s feed that have new messages since the last time the user
accessed the system, or all threads in her friend feed that have unread messages, or all messages containing the words of interest  across all feeds that the user can access.
Additionally, users can also search for posts that were posted within a geographic radius by providing the desired distance in miles.

# Technologies used:
1. Flask - Web framework and backend
2. PostgreSql - database
3. HTML / CSS - frontend design
4. Javascript - frontend scripts

