insert into hood values(1, 'Sunset Park', 40.65293489475142, -74.01186072158399, 1);
insert into hood values(2, 'Bayridge', 40.6268109112397, -74.03076959870124, 1);

select * from hood;
-- Bayridge
insert into block values(1, 'Ridge blvd 84th - 86th', 2, 40.62493325478114, -74.03339654572974, 0.15);
insert into block values(2, '4th avenue 84th - 86th', 2, 40.623679212056345, -74.02807504302626, 0.163);
insert into block values(3, 'Ridge blvd 81st - 83rd', 2, 40.62700853707446, -74.03259569372335, 0.15);
insert into block values(4, '4th avenue 81st - 83rd', 2, 40.62577896219109, -74.02719908909059, 0.163);

-- Sunset Park
insert into block values(5, '4th avenue 52nd - 54th', 1, 40.64483215711303, -74.01434417342031, 0.13);
insert into block values(6, '6th avenue 52nd - 54th', 1, 40.64210709975797, -74.00987752551411, 0.15);

select * from block;


-- Block Request
insert into user_block_req values('brucebutler', 1, 0, 0, now() ,0);

insert into user_block_req values('liamsimons', 1, 0, 0, now(), 0);

insert into user_block_req values('brucebutler', 2, 0, 0, now(), 0);

insert into user_block_req values('markmathew', 2, 0, 0, now(), 0);

-- have to set the mem_count to 0 for the queries to work
select * from user_block_req;


-- Thread messgaes
insert into thread(title, description, username, f_username, all_friends, block_feed, hood_feed, create_timestamp, updated_timestamp) 
values('selling bikes',' selling used bikes', 'brucebutler', 'liamsimons', 0, null, null, now(), now());

insert into thread(title, description, username, f_username, all_friends, block_feed, hood_feed, create_timestamp, updated_timestamp) 
values('spare parts', 'bike spare parts for sale', 'brucebutler', null, 1, null, null, now(), now());

insert into thread(title, description, username, f_username, all_friends, block_feed, hood_feed, create_timestamp, updated_timestamp) 
values('block message', 'block message check', 'brucebutler', null, 0, (select bid from user_block where username = 'brucebutler' and member_or_follower = 1), null, now(), now());

insert into thread(title, description, username, f_username, all_friends, block_feed, hood_feed, create_timestamp, updated_timestamp) 
values('block message 2', 'block message check 2', 'brucebutler', null, 0, (select bid from user_block where username = 'brucebutler' and member_or_follower = 1), null, now(), now());

insert into thread(title, description, username, f_username, all_friends, block_feed, hood_feed, create_timestamp, updated_timestamp) 
values('hood 1', 'hood message check', 'brucebutler', null, 0, 0, (select hood_id from user_hood where username = 'brucebutler'), now(), now());

insert into thread(title, description, username, f_username, all_friends, block_feed, hood_feed, create_timestamp, updated_timestamp) 
values('selling chair',' selling used chair', 'brucebutler', 'liamsimons', 0, null, null, now(), now());


-- Neighbor
insert into neighbor values('brucebutler', 'adeleneflores');
insert into neighbor values('liamsimons', 'markmathew');
insert into neighbor values('liamsimons', 'brucebutler');




