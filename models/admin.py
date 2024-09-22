from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for
from flask_login import current_user

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))
    
class UserAdmin(AdminModelView):
    column_list = ('id', 'data', 'user_id', 'starred')
    column_filters = ('starred', 'user_id')

class TradeHistoryAdmin(AdminModelView):
    column_list = ('id', 'login', 'email', 'email_confirmed', 'name', 'google_user',
                   'original_google_picture', 'about', 'picture', 'creation_date', 
                   'last_login', 'role')
    column_filters = ('login', 'email', 'name', 'google_user', 'about', 'role')
    form_excluded_columns = ('password_hash',)

class SettingsAdmin(AdminModelView):
    column_list = ('id', 'data', 'user_id', 'starred')
    column_filters = ('starred', 'user_id')