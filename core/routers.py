class DatabaseRouter:
    # route_app_labels = {'users':'users_db','products':'products_db','orders':'orders_db'}

    # def db_for_read(self,model,**hints):
    #     if model._meta.app_label in self.route_app_labels:
    #         return self.route_app_labels[model._meta.app_label]
    #     return None
    
    # def db_for_write(self,model,**hints):
    #     if model._meta.app_label in self.route_app_labels:
    #         return self.route_app_labels[model._meta.app_label]
    #     return None
    
    # def allow_relation(self,obj1,obj2,**hints):
    #     return True
    
    # def allow_migrate(self,db,app_label,model_name=None,**hints):
    #     if app_label in self.route_app_labels:
    #         return db == self.route_app_labels[app_label]
    #     return None

    def db_for_read(self,model,**hints):
        if model._meta.app_label == 'core':
            if model.__name__ == 'User':
                return 'users_db'
            elif model.__name__ == 'Product':
                return 'products_db'
            elif model.__name__ == 'Order':
                return 'orders_db'
        return None
    
    def db_for_write(self,model,**hints):
        if model._meta.app_label == 'core':
            if model.__name__ == 'User':
                return 'users_db'
            elif model.__name__ == 'Product':
                return 'products_db'
            elif model.__name__ == 'Order':
                return 'orders_db'
        return None
    
    def allow_relation(self,obj1,obj2,**hints):
        return True
    
    def allow_migrate(self,db,app_label,model_name=None,**hints):
        if app_label == 'core':
            if model_name == 'user':
                return db == 'users_db'
            elif model_name == 'product':
                return db == 'products_db'
            elif model_name == 'order':
                return db == 'orders_db'
        return None
            