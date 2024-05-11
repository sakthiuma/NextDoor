import datetime
import hashlib

from flask import Flask, render_template, url_for, flash, redirect, session, request
from geopy import Nominatim

from database.connection import get_db_connection
from forms import RegistrationForm, LoginForm, PostThreadForm, ThreadReplyForm, SearchForm, AddNeighborForm, \
    AddFriendForm, AddBlockForm, ForgotPasswordForm, AddressUpdateForm, DescriptionUpdateForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '7860db5e94eb7e89dc7a600f77452176'

@app.route('/profile', methods=['GET', 'POST'])
def user_profile():
    form = AddressUpdateForm()
    form2 = DescriptionUpdateForm()
    with conn.cursor() as cursor:
        get_user_info_sql = (" select * from user_rec where username='{user}' ").format(user=session['username'])
        cursor.execute(get_user_info_sql)
        user=[]
        for val in cursor.fetchall():
            user.append({
                'username' : val[0],
                'name': ("{first} {last}").format(first=val[1], last=val[2]),
                'address': ("{hno}, {street}, {city}, {state}, {pin}").format(hno=val[3], street=val[4], city=val[6],
                                                                              state=val[7], pin=val[8]),
                'desc': val[-1]
            })

    if form.validate_on_submit():
        with conn.cursor() as cursor:
            add = str(
                form.houseno.data) + " " + form.streetadd.data + " " + form.city.data + " " + form.state.data + " " + str(
                form.zipcode.data)

            getLoc = loc.geocode(add)
            lat = getLoc.latitude
            long = getLoc.longitude
            update_add_sql = ("update user_rec"
                              " set houseno=%s, street_add=%s, apt_no=%s, city= %s, state = %s, zipcode=%s, "
                              "latitude=%s, longitude=%s"
                              " where username=%s")
            cursor.execute(update_add_sql, (form.houseno.data, form.streetadd.data, form.aptno.data, form.city.data,
                                            form.state.data, form.zipcode.data, lat, long, session['username']))
            conn.commit()
            return redirect(url_for('user_profile'))

    if form2.validate_on_submit():
        with conn.cursor() as cursor:
            update_desp_sql = (" update user_rec"
                               " set description = %s"
                               " where username = %s")

            cursor.execute(update_desp_sql, (form2.description.data, session['username']))
            conn.commit()
            return redirect(url_for('user_profile'))

    return render_template('profile.html', username=session['username'], user=user, form = form,
                           form2=form2)




@app.route("/friend", methods=['GET', 'POST'])
def friend_feed():
    with conn.cursor() as cursor:
        friend_feed = ("select distinct t.title as title, t.description as description, 1 as member_or_follower, "
                       " t.thread_id as thread_id, t.username as author, t.create_timestamp as date_posted"
                       " from thread as t left outer join user_thread_read_timestamp using (thread_id, username)"
                       " where (f_username = %s or (all_friends = 1 and t.username in (select username from user_friend where f_username = %s)))  "
                       " and (create_timestamp > (select last_visit_timestamp from user_last_visit where username = %s)"
                       " or (read_timestamp is null or read_timestamp <= updated_timestamp))")
        cursor.execute(friend_feed, (session['username'], session['username'], session['username']))
        posts=[]
        for val in cursor.fetchall():
            posts.append({
                'id': val[3],
                'author': val[4],
                'title': val[0],
                'content': val[1],
                'date_posted': val[-1].strftime("%Y-%m-%d %H:%M:%S"),
                'member_or_follower': val[2]
            })

    with conn.cursor() as cursor:
        curr_friend_sql = ("select f_username from user_friend"
                           " where username='{user}'").format(user=session['username'])
        cursor.execute(curr_friend_sql)
        friend_users = []
        for val in cursor.fetchall():
            friend_users.append({
                'username': val[0]
            })

    form = AddFriendForm()
    with conn.cursor() as cursor:
        get_new_friends = (" select username from user_rec"
                            " where not username='{user}'"
                            " except"
                            " select f_username"
                            " from user_friend"
                            " where username = '{user}'").format(user=session['username'])
        cursor.execute(get_new_friends)
        add_friend_res = [i[0] for i in cursor.fetchall()]
        add_friend_res.insert(0, '')
        add_friend_res = [(value, value) for index, value in enumerate(add_friend_res)]

    with conn.cursor() as cursor:
        get_pending_req_sql = ("select * from user_friend_req"
                               " where f_username='{user}'"
                               " and status = 'pending'").format(user=session['username'])

        cursor.execute(get_pending_req_sql)
        friend_reqs=[]
        for val in cursor.fetchall():
            friend_reqs.append({
                'username': val[0]
            })

    form.f_username.choices=add_friend_res

    if form.validate_on_submit():
        with conn.cursor() as cursor:
            insert_friend_req_sql = ("insert into user_friend_req(username, f_username, status) "
                                     " values('{curr_user}', '{f_user}', 'pending')").format(curr_user=session['username'],
                                                                                             f_user=form.f_username.data)
            cursor.execute(insert_friend_req_sql)
            conn.commit()
            flash(f'Sent friend req to {form.f_username.data}', category='success')
            return redirect(url_for('friend_feed'))

    return render_template('/feed/friend.html', posts=posts, username=session['username'], form=form,
                           f_users = friend_users, pending_reqs= friend_reqs)


@app.route("/accept_req/<from_username>", methods=['GET', 'POST'])
def accept_friend_req(from_username):
    with conn.cursor() as cursor:
        accept_friend_req_sql = ("update user_friend_req"
                                  " set status = 'accepted'"
                                  " where username = '{from_user}' and f_username = '{to}'").format(from_user= from_username,
                                        to=session['username'])
        cursor.execute(accept_friend_req_sql)
        conn.commit()
    return redirect(url_for('friend_feed'))

@app.route("/neighbor", methods = ['GET', 'POST'])
def neighbor_feed():
    with conn.cursor() as cursor:
        neigh_feed = ("select distinct t.title as title, t.description as description, 1 as member_or_follower, "
                       " t.thread_id as thread_id, t.username as author, t.create_timestamp as date_posted"
                       " from thread as t left outer join user_thread_read_timestamp using (thread_id, username)"
                       " where (neigh_username = %s or (all_neigh = 1 and t.username in (select username from neighbor "
                      " where neigh_username = %s)))  "
                       " and (create_timestamp > (select last_visit_timestamp from user_last_visit where username = %s)"
                       " or (read_timestamp is null or read_timestamp <= updated_timestamp))")
        cursor.execute(neigh_feed, (session['username'], session['username'], session['username']))
        posts=[]
        for val in cursor.fetchall():
            posts.append({
                'id': val[3],
                'author': val[4],
                'title': val[0],
                'content': val[1],
                'date_posted': val[-1].strftime("%Y-%m-%d %H:%M:%S"),
                'member_or_follower': val[2]
            })


    with conn.cursor() as cursor:
        curr_neigh_sql = ("select neigh_username from neighbor"
                          " where username='{curr_user}'").format(curr_user=session['username'])
        cursor.execute(curr_neigh_sql)
        neigh_users = []
        for val in cursor.fetchall():
            neigh_users.append({
                'neighbor': val[0]
            })

    form = AddNeighborForm()

    with conn.cursor() as cursor:
        add_neighbor_sql = (" select username from user_block where not username='{curr_user}'"
                            " and bid in(select bid from user_block where username = '{curr_user}'"
                            " and member_or_follower=1)"
                            " and member_or_follower=1"
                            " except"
                            " select neigh_username from neighbor where username='{curr_user}'").format(
            curr_user=session['username'])
        cursor.execute(add_neighbor_sql)
        add_neigh_res = [i[0] for i in cursor.fetchall()]
        add_neigh_res.insert(0, '')
        add_neigh_res = [(value, value) for index, value in enumerate(add_neigh_res)]

    form.neigh_username.choices = add_neigh_res

    if form.validate_on_submit():
        with conn.cursor() as cursor:
            insert_neigh_sql = ("insert into neighbor(username, neigh_username)"
                                " values('{curr_user}', '{neigh_user}')").format(curr_user=session['username'],
                                                                             neigh_user=form.neigh_username.data)
            cursor.execute(insert_neigh_sql)
            conn.commit()
            flash(f"Added {form.neigh_username.data} as your neighbor", category='success')
            return redirect(url_for('neighbor_feed'))

    return render_template('/feed/neigh.html', posts=posts, username=session['username'],
                           neigh_users=neigh_users, form=form)

@app.route("/hood", methods=['GET', 'POST'])
def hood_feed():
    with conn.cursor() as cursor:
        hood_sql = ("select distinct t.title as title, t.description as description, uh.member_or_follower, "
                    " t.thread_id as thread_id,  t.username as author, t.create_timestamp as date_posted "
                    "from thread as t left outer join user_thread_read_timestamp using (thread_id, username) "
                    "join user_hood as uh on uh.hood_id = t.hood_feed "
                    "where uh.username = %s and "
                    "(create_timestamp > (select last_visit_timestamp from user_last_visit where username = %s) "
                    "or (read_timestamp is null or read_timestamp <= updated_timestamp))")
        cursor.execute(hood_sql, (session['username'], session['username']))
        posts = []
        for val in cursor.fetchall():
            posts.append({
                'id': val[3],
                'author': val[4],
                'title': val[0],
                'content': val[1],
                'date_posted': val[-1].strftime("%Y-%m-%d %H:%M:%S"),
                'member_or_follower': val[2],
            })

    with conn.cursor() as cursor:
        mem_hood_sql = ("select hname from hood "
                        " where hood_id in (select hood_id from user_hood where username = '{user}')").format(user=session['username'])
        cursor.execute(mem_hood_sql)
        mem_hood = []
        for val in cursor.fetchall():
            mem_hood.append({
                'hname': val[0]
            })
    return render_template('/feed/hood.html', posts=posts, username=session['username'],
                           curr_member_hood=mem_hood)

@app.route("/block", methods=['GET', 'POST'])
def block_feed():
    with conn.cursor() as cursor:
        block_sql = ("select distinct t.title as title, t.description as description, "
                     "ub.member_or_follower, t.thread_id as thread_id,  "
                     "t.username as author, t.create_timestamp as date_posted "
                     "from thread as t "                   
                     "left outer join user_thread_read_timestamp using (thread_id, username) "
                     "join user_block as ub on ub.bid = t.block_feed "
                     "where ub.username = %s and "
                     "(create_timestamp > (select last_visit_timestamp from user_last_visit where username = %s) "
                     "or (read_timestamp is null or read_timestamp <= updated_timestamp))")
        cursor.execute(block_sql, (session['username'], session['username']))
        posts = []
        for val in cursor.fetchall():
            posts.append({
                'id': val[3],
                'author': val[4],
                'title': val[0],
                'content': val[1],
                'date_posted': val[-1].strftime("%Y-%m-%d %H:%M:%S"),
                'member_or_follower': val[2]
            })
    with conn.cursor() as cursor:
        member_blk_sql = ("select description, bid from block"
                          " where bid in (select bid from user_block where username='{user}'"
                          "and member_or_follower= 1)").format(user=session['username'])
        cursor.execute(member_blk_sql)
        curr_member_blk = []
        for val in cursor.fetchall():
            curr_member_blk.append({
                'bname' : val[0],
                'bid': val[1]
            })

    with conn.cursor() as cursor:
        follow_blk_sql = ("select description, bid from block"
                          " where bid in (select bid from user_block where username='{user}'"
                          "and member_or_follower=2)").format(user=session['username'])
        cursor.execute(follow_blk_sql)
        follow_blk = []
        for val in cursor.fetchall():
            follow_blk.append({
                'bname' : val[0],
                'bid': val[1]
            })


    #  do the pending block request
    with conn.cursor() as cursor:
        pending_blk_req_sql = (" select username from user_block_req"
                               " where bid in (select bid from user_block where username='{user}'"
                               " and member_or_follower=1)"
                               " and username not in (select req_username"
                               " from user_approve_block_req where approve_username = '{user}'"
                               " and bid in (select bid from user_block where username='{user}' and"
                               " member_or_follower=1))").format(user=session['username'])
        cursor.execute(pending_blk_req_sql)
        pending_blk_req = []
        for val in cursor.fetchall():
            pending_blk_req.append({
                'username': val[0]
            })


    form = AddBlockForm()
    with conn.cursor() as cursor:
        blks_to_join_sql = ("select description from block"
                            " where bid not in (select bid from user_block"
                            " where username = '{curr_user}' and (member_or_follower=1 or member_or_follower=2))").format(
            curr_user=session['username'])
        cursor.execute(blks_to_join_sql)
        blks_to_join = []

        blks_to_join = [i[0] for i in cursor.fetchall()]
        blks_to_join.insert(0, '')
        blks_to_join = [(value, value) for index, value in enumerate(blks_to_join)]

    form.bname.choices = blks_to_join

    if form.validate_on_submit():
        with conn.cursor() as cursor:
            ins_blk_req_sql = (" insert into user_block_req (username, bid, mem_count, approval_count, req_timestamp, "
                               "deny_count) "
                               "values('{user}', (select bid from block where"
                               " description = '{desp}'), (select mem_count from block where description='{desp}'),"
                               "0, '{curr_time}', 0)").format(user=session['username'], desp=form.bname.data,
                                                            curr_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            cursor.execute(ins_blk_req_sql)
            conn.commit()
            flash(f" Sent block request for approval from other members. You will be a member "
                  f"once you are approved. If not, you will be allowed to follow the group ", category='success')


    return render_template('/feed/block.html', posts=posts, username=session['username'],
                        curr_member_blk=curr_member_blk, follow_blk=follow_blk,
                           pending_blk_req=pending_blk_req, form=form)

@app.route('/accept_block_req/<from_username>', methods=['GET', 'POST'])
def accept_block_req(from_username):
    with conn.cursor() as cursor:
        insert_app_sql = (" insert into user_approve_block_req(req_username, approve_username, bid, status)"
                          " values('{user}', '{curr_user}', (select bid from user_block where username = '{curr_user}'"
                          " and member_or_follower=1), 'approved')").format(user=from_username, curr_user=session['username'])
        cursor.execute(insert_app_sql)
        conn.commit()
    with conn.cursor() as cursor:
        accept_block_req_sql = ("update user_block_req"
                                " set approval_count = approval_count +1 "
                                " where username='{user}' and bid in (select bid from user_block where username='{curr_user}'"
                                "and member_or_follower=1)").format(user=from_username, curr_user=session['username'])
        cursor.execute(accept_block_req_sql)
        conn.commit()
    return redirect(url_for('block_feed'))


@app.route('/remove_block_req/<blk_id>', methods=['GET', 'POST'])
def remove_block_req(blk_id):
    with conn.cursor() as cursor:
        remove_block_req_sql = ("delete from user_block "
                                " where username='{user}' and bid = {blk_id}").format(user=session['username'], blk_id=blk_id)
        cursor.execute(remove_block_req_sql)
        conn.commit()
    return redirect(url_for('block_feed'))

@app.route("/your_threads")
def your_threads():
    with conn.cursor() as cursor:
        your_threads_sql = "select * from thread where username=%s"
        cursor.execute(your_threads_sql, (session['username'],))
        posts = []
        for val in cursor.fetchall():
            posts.append({
                'id': val[0],
                'author': val[3],
                'title': val[1],
                'content': val[2],
                'date_posted': val[8].strftime("%Y-%m-%d %H:%M:%S"),
                'member_or_follower': 1
            })
    return render_template('/feed/your_feed.html', posts= posts, username=session['username'])

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with conn.cursor() as cursor:
            check_exis_rec_sql = (" select * from user_rec where username = '{user}'").format(user=form.username.data)
            cursor.execute(check_exis_rec_sql)
            if cursor.fetchone():
                flash(f'Account already exists for {form.username.data}. Please login with the original '
                      f'credentials else try a different username', 'warning')
                return redirect('register')


        with conn.cursor() as cursor:
            user_rec_sql = ("INSERT INTO user_rec "
                   "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            add = str(form.houseno.data) + " " + form.streetadd.data + " " + form.city.data + " " + form.state.data + " " + str(form.zipcode.data)

            getLoc = loc.geocode(add)
            lat = getLoc.latitude
            long = getLoc.longitude
            affected_rows = cursor.execute(user_rec_sql, (form.username.data, form.firstname.data, form.lastname.data, form.houseno.data,
                                                          form.streetadd.data, form.aptno.data, form.city.data, form.state.data, form.zipcode.data,
                                                          lat, long, form.description.data))

            conn.commit()

            user_cred_sql = "INSERT INTO user_creds VALUES(%s, %s)"
            password_hash = hashlib.sha256(form.password.data.encode('utf-8')).hexdigest()
            cursor.execute(user_cred_sql, (form.username.data, password_hash))
            conn.commit()

            session['username'] = form.username.data

            print(f"Account Creation, inserted {affected_rows}")

        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('friend_feed'))
    return render_template('register.html', title='Register', form=form)


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with conn.cursor() as cursor:
            sql = "SELECT * FROM user_creds WHERE username=%s and password=%s"
            password_hash = hashlib.sha256(form.password.data.encode('utf-8')).hexdigest()
            cursor.execute(sql, (form.username.data, password_hash))
            if cursor.fetchone() == None:
                flash('Incorrect credentials', 'warning')
            else:
                session['username'] = form.username.data
                conn.commit()
                return redirect(url_for('friend_feed'))
    return render_template('login.html', title='Login', form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        with conn.cursor() as cursor:
            update_password_sql = ("update user_creds"
                                   " set password=%s"
                                   " where username = %s")
            password_hash = hashlib.sha256(form.password.data.encode('utf-8')).hexdigest()
            cursor.execute(update_password_sql, (password_hash, form.username.data))
            conn.commit()
            session['username'] = form.username.data
        return redirect(url_for('friend_feed'))
    return render_template('forgot_password.html', title='Forgot Password', form = form)

@app.route("/post/thread", methods=['GET', 'POST'])
def new_thread():
    form = PostThreadForm()
    with conn.cursor() as cursor:
        all_friend_sql = ("SELECT f_username FROM user_friend where username = %s")
        cursor.execute(all_friend_sql, (session['username'],))
        all_friends = [i[0] for i in cursor.fetchall()]
        all_friends.insert(0, '')
        all_friends = [(value, value) for index, value in enumerate(all_friends)]

        all_neigh_sql = ("SELECT neigh_username FROM neighbor WHERE username = %s")
        cursor.execute(all_neigh_sql, (session['username'],))
        all_neigh = [i[0] for i in cursor.fetchall()]
        all_neigh.insert(0, '' )
        all_neigh = [(value, value) for index, value in enumerate(all_neigh)]

    form.f_username.choices = all_friends
    form.neigh_username.choices = all_neigh
    if request.method == 'GET':
        return render_template('create_thread.html', title='New thread', form=form)
    else :
        if form.validate_on_submit():
            to_all_friends = 0
            to_all_neigh = 0
            bid = None
            hid = None
            f_user = None
            neigh_user = None
            if form.f_username.data != '':
                f_user = form.f_username.data
            if form.neigh_username.data != '':
                neigh_user = form.neigh_username.data
            if form.all_friend.data:
                to_all_friends = 1
            if form.all_neigh.data:
                to_all_neigh = 1
            if form.to_block.data:
                with conn.cursor() as cursor:
                    bid_sql = "SELECT bid from user_block where username=%s and member_or_follower=1"
                    cursor.execute(bid_sql, (session['username'],))
                    bid = cursor.fetchone()
            if form.to_hood.data:
                with conn.cursor() as cursor:
                    hid_sql = "SELECT hood_id from user_hood where username=%s and member_or_follower=1"
                    cursor.execute(hid_sql, (session['username'],))
                    hid = cursor.fetchone()
            with conn.cursor() as cursor:
                thread_sql = ("insert into thread(title, description, username, f_username, neigh_username,"
                              " all_friends, all_neigh, block_feed, hood_feed, "
                              "create_timestamp, updated_timestamp) "
                              "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                cursor.execute(thread_sql, (form.title.data, form.content.data, session['username'], f_user,
                                            neigh_user, to_all_friends, to_all_neigh, bid, hid,
                                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
            print(form.neigh_username.data, form.f_username.data, form.to_hood.data)
            return redirect(url_for("friend_feed"))
        return render_template('create_thread.html', title='New thread', form=form)

@app.route("/thread/<int:thread_id>/<int:member_or_follower>", methods=['GET', 'POST'])
def thread(thread_id, member_or_follower):
    form = ThreadReplyForm()
    with conn.cursor() as cursor:
        get_thread_sql = "SELECT * from thread where thread_id=%s"
        cursor.execute(get_thread_sql, (thread_id,))
        thread = cursor.fetchone()
    with conn.cursor() as cursor:
        get_replies_sql = "select * from thread_message where thread_id=%s"
        cursor.execute(get_replies_sql, (thread_id,))
        replies = cursor.fetchall()

    thread_with_replies = []
    return_replies = []
    for rep in replies:
        return_replies.append({
            'reply_username': rep[1],
            'reply_msg': rep[3],
            'reply_date_posted': rep[2].strftime("%Y-%m-%d %H:%M:%S")
        })

    thread_with_replies.append({
        'title': thread[1],
        'content': thread[2],
        'author': thread[3],
        'date_posted': thread[8].strftime("%Y-%m-%d %H:%M:%S"),
        'replies': return_replies,
        'member_or_follower': member_or_follower
    })
    with conn.cursor() as cursor:
        thread_read_time_sql = ("insert into user_thread_read_timestamp(username, thread_id, read_timestamp)"
                                "values(%s, %s, %s)"
                                "on conflict (username, thread_id) do update set read_timestamp=%s")
        cursor.execute(thread_read_time_sql,
                       (session['username'], thread_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

    if form.validate_on_submit():
        with conn.cursor() as cursor:
            insert_msg_sql = ("insert into thread_message(username, created_timestamp, body, thread_id)"
                                  "values(%s, %s, %s, %s)")
            cursor.execute(insert_msg_sql, (session['username'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                form.content.data, thread_id))
            conn.commit()
        with conn.cursor() as cursor:
            update_thread_time_sql = "update thread set updated_timestamp=%s where thread_id=%s"
            cursor.execute(update_thread_time_sql, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), thread_id))


        return redirect(url_for('thread', thread_id=thread_id, member_or_follower=member_or_follower))

    return render_template('post.html', title="post", threads=thread_with_replies, form=form)


@app.route("/search", methods=['GET', 'POST'])
def search_messages():
    form = SearchForm()
    if form.validate_on_submit():
        if form.text_search.data != '':
            with conn.cursor() as cursor:
                text_search_sql = ("select distinct alias.title as title, alias.description as description, alias.member_or_follower"
                                   " as member_or_follower, alias.thread_id as thread_id, "
                                   " alias.author as author, alias.date_posted as date_posted from ("                               
                                   " select t.title as title, t.description as description, 1 as member_or_follower, "                               
                                   " t.thread_id as thread_id, t.username as author, t.create_timestamp as date_posted,"
                                   " m.body as message_body"
                                   " from thread as t left outer join user_thread_read_timestamp using (thread_id)"
                                   " left outer join thread_message as m using (thread_id) "
                                   " where (f_username = '{user}' or (all_friends = 1 and t.username in (select username "
                                   " from user_friend where f_username = '{user}')))  "
                                   " union "
                                   " select t.title as title, t.description as description, 1 as member_or_follower, "
                                   " t.thread_id as thread_id, t.username as author, t.create_timestamp as date_posted,"
                                   " m.body as message_body"
                                   " from thread as t left outer join user_thread_read_timestamp using (thread_id)"
                                   " left outer join thread_message as m using (thread_id) "
                                   " where (neigh_username = '{user}' or (all_neigh = 1 and t.username in (select username from "
                                   " neighbor where neigh_username = '{user}')))  "
                                   " union "
                                   "select t.title as title, t.description as description, uh.member_or_follower, "
                                   " t.thread_id as thread_id,  t.username as author, t.create_timestamp as date_posted, "
                                   " m.body as message_body"
                                   " from thread as t left outer join user_thread_read_timestamp using (thread_id) "
                                   " left outer join thread_message as m using (thread_id) "
                                   " join user_hood as uh on uh.hood_id = t.hood_feed "
                                   " where uh.username = '{user}' "
                                   " union "
                                   " select t.title as title, t.description as description, "
                                   " ub.member_or_follower, t.thread_id as thread_id,  "
                                   " t.username as author, t.create_timestamp as date_posted, "
                                   " m.body as message_body"
                                   " from thread as t "                   
                                   " left outer join user_thread_read_timestamp using (thread_id) "
                                   " join user_block as ub on ub.bid = t.block_feed "
                                   " left outer join thread_message as m using (thread_id) "
                                   " where ub.username = '{user}'"
                                   ") as alias "
                                   " where alias.description like '%{text}%' or alias.title like '%{text}%' or "
                                   "alias.message_body like '%{text}%' ").format(text=form.text_search.data, user=session['username'])
                cursor.execute(text_search_sql)

                posts=[]
                for val in cursor.fetchall():
                    posts.append({
                        'id': val[3],
                        'author': val[4],
                        'title': val[0],
                        'content': val[1],
                        'date_posted': val[-1].strftime("%Y-%m-%d %H:%M:%S"),
                        'member_or_follower': val[2]
                    })
                return render_template('search.html',posts=posts, username=session['username'], form=form)
        elif form.loc_search.data != 0:
            with conn.cursor() as cursor:
                loc_search_sql = ("select * from ( select distinct t.title as title, t.description as description, "
                                  " 1 as member_or_follower, t.thread_id as thread_id, "
                                  " ST_DistanceSphere(ST_MakePoint(b.longitude, b.latitude),ST_MakePoint(ur.longitude, ur.latitude))/1609 as distance_in_miles, "
                                  " t.username as author, t.create_timestamp as date_posted "
                                  " from thread  t "
                                  " join block b on b.bid = t.block_feed "
                                  " cross join user_rec ur where ur.username = '{user}'"
                                  " union all "
                                  " select distinct t.title as title, t.description as description, 1 as member_or_follower,"
                                  " t.thread_id as thread_id, "
                                  " ST_DistanceSphere(ST_MakePoint(h.longitude, h.latitude),ST_MakePoint(ur.longitude, ur.latitude))/1609 as distance_in_miles, "
                                  " t.username as author, t.create_timestamp as date_posted "
                                  " from thread  t "
                                  " join hood h on h.hood_id = t.hood_feed "
                                  " cross join user_rec ur "
                                  "where ur.username = '{user}')"
                                  " as alias where alias.distance_in_miles <= {dist} ").format(user=session['username'], dist=form.loc_search.data)
                cursor.execute(loc_search_sql)
                posts=[]
                for val in cursor.fetchall():
                    posts.append({
                        'id': val[3],
                        'author': val[5],
                        'title': val[0],
                        'content': val[1],
                        'date_posted': val[-1].strftime("%Y-%m-%d %H:%M:%S"),
                        'member_or_follower': val[2]
                    })
                return render_template('search.html', posts=posts, username=session['username'], form=form)
    return render_template('search.html', username=session['username'], form=form)


@app.route("/add_neigh")
def add_neighbor():
    form = AddNeighborForm()

    with conn.cursor() as cursor:
        add_neighbor_sql = (" select username from user_block where not username={curr_user}"
                            "and bid in(select bid from user_block where username = {curr_user}"
                            "and member_or_follower=1)"
                            "and member_or_follower=1"
                            "except"
                            "select neigh_username from neighbor where username={curr_user}").format(curr_user=session['username'])
        cursor.execute(add_neighbor_sql)
        add_neigh_res = [i[0] for i in cursor.fetchall()]
        add_neigh_res.insert(0, '')
        add_neigh_res = [(value, value) for index, value in enumerate(add_neigh_res)]

    form.neigh_username.choices = add_neigh_res

    with conn.cursor() as cursor:
        curr_neigh_sql = ("select neigh_username from neighbor"
                          "where username={curr_user}").format(curr_user=session['username'])

    if form.validate_on_submit():
        with conn.cursor() as cursor:
            insert_neigh_sql =("insert into neighbor(username, neigh_username)"
                               " values({curr_user}, {neigh_user})").format(curr_user=session['username'],
                                                                            neigh_user=form.neigh_username.data)
            cursor.execute(insert_neigh_sql)
            conn.commit()
            return redirect(url_for('add_neighbor'))
    return render_template('/')



@app.route("/logout")
def logout():
    with conn.cursor() as cursor:
        last_visit_sql = ("insert into user_last_visit(username, last_visit_timestamp)"
                          "values(%s, %s) on conflict(username) do update set last_visit_timestamp=%s")
        cursor.execute(last_visit_sql, (session['username'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    global conn
    conn = get_db_connection()
    global loc
    loc = Nominatim(user_agent="Geopy Library")
    app.run(debug=True)