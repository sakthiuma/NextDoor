create extension postgis;

create table hood (
	hood_id int primary key,
	hname varchar(25),
	latitude numeric,
	longitude numeric,
	radius numeric
);

create table block (
	bid int primary key,
	description varchar(50),
	hood_id int,
	latitude numeric,
	longitude numeric,
	radius numeric,
	mem_count int,
	constraint b_fk_hood foreign key (hood_id) references hood(hood_id)	
);

create table user_rec(
	username varchar(50) primary key,
	firstname varchar(25),
	lastname varchar(25),
	houseno int,
	street_add varchar(50),
	apt_no int,
	city varchar(25),
	state varchar(25),
	zipcode varchar(25),
	latitude numeric,
	longitude numeric,
	description varchar(100)
);

create table user_creds(
	username varchar(50) primary key,
	password varchar(255),
	constraint uc_fk_username foreign key(username) references user_rec(username)
);

create table user_friend_req(
	username varchar(50),
	f_username varchar(50),
	status varchar(25),
	primary key(username, f_username),
	constraint ufr_fk_username foreign key(username) references user_rec(username),
	constraint ufr_fk_fusername foreign key(f_username) references user_rec(username)
);

create table user_friend(
	username varchar(50),
	f_username varchar(50),
	primary key(username, f_username),
	constraint uf_fk_username foreign key(username) references user_rec(username),
	constraint uf_fk_fusername foreign key(f_username) references user_rec(username)
);

create table user_block_req (
	username varchar(50),
	bid int,
	mem_count int,
	approval_count int,
	req_timestamp timestamp,
	deny_count int,
	primary key(username, bid),
	constraint ubr_fk_username foreign key(username) references user_rec(username),
	constraint ubr_fk_bid foreign key (bid) references block(bid)
);

create table user_block(
	username varchar(50),
	bid int,
	member_or_follower int,
	primary key(username, bid),
	constraint ub_fk_username foreign key(username) references user_rec(username),
	constraint ub_fk_bid foreign key (bid) references block(bid)
);

create table user_hood(
	username varchar(50),
	hood_id int,
	member_or_follower int,
	primary key(username, hood_id),
	constraint uh_fk_username foreign key(username) references user_rec(username),
	constraint uh_fk_hood_id foreign key (hood_id) references hood(hood_id)
);

create table user_approve_block_req (
	req_username varchar(50),
	approve_username varchar(50),
	bid int,
	status varchar(25),
	primary key(req_username, approve_username, bid),
	constraint upbr_fk_approve_username foreign key(approve_username) references user_rec(username),
	constraint upbr_fk_req_username foreign key(req_username) references user_rec(username),
	constraint upbr_fk_bid foreign key(bid) references block(bid)
);

create table user_last_visit(
	username varchar(50),
	last_visit_timestamp timestamp,
	primary key(username),
	constraint ulv_fk_username foreign key(username) references user_Rec(username)
);

create unique index user_last_visit_index on user_last_visit(username);

create table thread(
	thread_id int primary key generated by default as identity,
	title varchar(50),
	description varchar(50),
	username varchar(50),
	f_username varchar(50), 
	all_friends int,
	block_feed int,
	hood_feed int,
	create_timestamp timestamp,
	updated_timestamp timestamp,
	constraint t_fk_username foreign key(username) references user_rec(username),
	constraint t_fk_f_username foreign key(f_username) references user_rec(username)
);

alter table thread
add column neigh_username varchar(50),
add column all_neigh int;

alter table thread
add constraint t_fk_neigh_username foreign key(neigh_username) references user_rec(username);

create table user_thread_read_timestamp(
	username varchar(50),
	thread_id int,
	read_timestamp timestamp,
	constraint utt_fk_username foreign key(username) references user_rec(username),
	constraint utt_fk_threadid foreign key(thread_id) references thread(thread_id)
);

create unique index user_thread_read_timestamp_unique on user_thread_read_timestamp(username, thread_id);

create table thread_message (
	mid int primary key generated by default as identity,
	username varchar(50),
	created_timestamp timestamp,
	body varchar(50),
	thread_id int,
	constraint m_fk_username foreign key(username) references user_rec(username),
	constraint m_fk_threadid foreign key(thread_id) references thread(thread_id)
);

create table neighbor(
	username varchar(50),
	neigh_username varchar(50),
	primary key(username, neigh_username),
	constraint n_fk_username foreign key(username) references user_rec(username),
	constraint n_fk_neighusername foreign key(neigh_username) references user_rec(username)
);











