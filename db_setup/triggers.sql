drop trigger if exists addUserFriendTrigger on user_friend_req;
drop function if exists addUserFriend;

create function addUserFriend()
returns trigger
language PLPGSQL
as
$$
begin
	if exists (select from user_friend_req ufr where ufr.username = new.username and ufr.f_username = new.f_username and ufr.status = 'accepted')
		and exists (select from user_friend_req ufr1 where ufr1.username = new.f_username and ufr1.f_username = new.username and ufr1.status= 'accepted') then
			insert into user_friend values (new.username, new.f_username);
			insert into user_friend values (new.f_username, new.username);
			
			return new;
	else
		return null;
	end if;
end;
$$

create trigger addUserFriendTrigger after insert or update on user_friend_req
for each row execute procedure addUserFriend();

drop trigger if exists userBlockReqTrigger on user_block_req;
drop function if exists userBlockReq;

create function userBlockReq()
returns trigger
language PLPGSQL
as
$$
begin
	if new.approval_count >= 3 or new.approval_count = new.mem_count then
		if not exists (select from user_block where username = new.username and member_or_follower = 1) then
			insert into user_block values (new.username, new.bid, 1);
			insert into user_hood values (new.username, (select hood_id from block where bid = new.bid), 1);
			delete from user_block_req where username = new.username and bid = new.bid;
			delete from user_approve_block_req where req_username = new.username and bid = new.bid;
			return new;
		else
			insert into user_block values (new.username, new.bid, 2);
			if not exists (select from user_hood where username = new.username and hood_id in (select hood_id from block where bid = new.bid)) then
				insert into user_hood values (new.username, (select hood_id from block where bid = new.bid), 2);
			end if;
			delete from user_block_req where username = new.username and bid = new.bid;
			delete from user_approve_block_req where req_username = new.username and bid = new.bid;
			return new;
		return new;
		
		end if;
	else 
		return null;
	end if;
end;
$$

create trigger userBlockReqTrigger after insert or update on user_block_req
for each row execute procedure userBlockReq();

drop trigger if exists updateMemCountTrigger on user_block;
drop function if exists updateMemCount;

create function updateMemCount()
returns trigger
language PLPGSQL
as
$$
begin
	if new.member_or_follower in (1) then
		update block
		set mem_count = mem_count+1
		where bid = new.bid;
	return new;
	end if;
	return null;
end;
$$

create trigger updateMemCountTrigger after insert or update on user_block
for each row execute procedure updateMemCount();

drop trigger if exists threadMessageAddTrigger on thread;
drop function if exists threadMessageAdd;

create function threadMessageAdd()
returns trigger
language PLPGSQL
as
$$
begin
	update thread
	set updated_timestamp = now()
	where thread_id = new.thread_id;
	return new;
end;
$$

create trigger threadMessageAddTrigger after insert or update on thread_message
for each row execute procedure threadMessageAdd();

drop trigger if exists removeNeighUserTrigger on user_block cascade;
drop function if exists removeNeighborUser cascade;

create function removeNeighborUser()
returns trigger
language PLPGSQL
as
$$
begin
	delete from neighbor
	where username = old.username;
		
	delete from neighbor
	where neigh_username = old.username;
	
	delete from user_hood
	where username = old.username;
	
	update block
	set mem_count = mem_count - 1
	where bid in (select bid from user_block
				 where username = old.username and old.member_or_follower = 1 and bid = old.bid);
	
-- 	delete from user_block_req 
-- 	where username = old.username;

	return old;
-- 	if (exists (select from neighbor where neigh_username = old.username) or 
-- 		exists (select from neighbor where username = old.username)) then
		
-- 	else
-- 		return null;	
-- 	end if;
end
$$

create trigger removeNeighborUserTrigger before delete on user_block
for each row execute procedure removeNeighborUser();




