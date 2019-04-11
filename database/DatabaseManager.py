from contextlib import contextmanager

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import update, delete
from sqlalchemy.orm import sessionmaker

from database.DatabaseModel import Url, Models, Trims
from database.DatabaseModel import Car

from database.DatabaseModel import Session

from helpers.timestamp_generator import generate_timestamp

from config import database_uri


class DatabaseManager():
    def __init__(self):
        self.dbPoolConnections = self.openConnection()

    def openConnection(self):
        myPool = create_engine(database_uri)
        return myPool

    def __del__(self):
        self.dbPoolConnections.dispose()

    @contextmanager
    def open_session(self):
        self.con = self.dbPoolConnections.connect()
        DBSession = sessionmaker(bind=self.con)
        session = DBSession()
        try:
            yield session
        finally:
            session.close()
            self.con.close()

    def insert_urls(self, urls_list, source):
        """:param urls_list - {'url': '', 'hash': '', 'proxie': ''}"""
        amount_of_existing = 0
        with self.open_session() as session:
            for url in urls_list:
                url_ = url['url']
                listing_id = url['listing_id']
                timestamp = generate_timestamp()
                new_url = Url(url=url_,
                              listing_id=listing_id,
                              processed=False,
                              active=True,
                              timestamp=timestamp,
                              source=source,
                              updated=0)
                try:
                    session.add(new_url)
                    session.flush()
                    session.commit()
                except Exception as exc:
                    print exc
                    amount_of_existing += 1
                    session.rollback()
        return {'amount_of_existing': amount_of_existing}

    def insert_data(self, data, listing_id, url, source):
        with self.open_session() as session:
            make = data['make']
            model = data['model']
            trim = data['trim']
            year = data['year']
            kilometres = data['kilometres']
            color = data['color']
            specs = data['specs']
            first_price = data['price']
            phone = data['phone']
            listing_id = listing_id
            timestamp = generate_timestamp()
            new_row = Car(make=make,
                          model=model,
                          trim=trim,
                          year=year,
                          km=kilometres,
                          color=color,
                          specs=specs,
                          first_price=first_price,
                          pc=first_price,
                          phone=phone,
                          listing_id=listing_id,
                          url=url,
                          timestamp=timestamp,
                          updated=False,
                          status="Active",
                          country=source,
                          days_on_market=1)
            try:
                session.add(new_row)
                session.commit()
            except Exception as exc:
                print exc
                session.rollback()
                return False

    def get_all_urls(self, source=None):
        urls_list = []

        with self.open_session() as session:
            if source is None:
                urls = session.query(Url).filter(Url.active == True).all()
            else:
                urls = session.query(Url).filter(Url.active == True,
                                                 Url.source == source).all()
            for url in urls:
                urls_list.append({'url': url.url,
                                  'id': url.id,
                                  'listing_id': url.listing_id,
                                  'timestamp': url.timestamp})
            return urls_list

    def get_all_listing_id(self):
        urls_list = []

        with self.open_session() as session:
            urls = session.query(Url).all()
            for url in urls:
                urls_list.append(url.listing_id)
            return urls_list

    def get_one_url(self, listing_id):
        urls_list = []

        with self.open_session() as session:
            url = session.query(Url).filter(Url.listing_id == listing_id).first()
            return {'url': url.url,
                    'id': url.id,
                    'listing_id': url.listing_id,
                    'timestamp': url.timestamp}

    def get_urls(self, source):
        urls_list = []
        with self.open_session() as session:
            urls = session.query(Url).filter(Url.processed == False,
                                             Url.active == True,
                                             Url.source == source
                                             ).all()
            for url in urls:
                urls_list.append({'url': url.url,
                                  'id': url.id,
                                  'listing_id': url.listing_id})
            return urls_list

    def get_car_data(self, listing_id):
        with self.open_session() as session:
            data = session.query(Car).filter(Car.listing_id == listing_id).first()
            return data

    def set_url_processed(self, url_id):
        with self.open_session() as session:
            smtp = update(Url).where(Url.id == url_id). \
                values(processed=True)
            session.execute(smtp)
            session.commit()

    def set_url_inactive(self, url_id):
        with self.open_session() as session:
            smtp = update(Url).where(Url.id == url_id). \
                values(active=False)
            session.execute(smtp)
            session.commit()

    def get_session_name(self, session_id):
        with self.open_session() as session:
            session_ = session.query(Session).filter(Session.id == session_id).first()
            session_ = session_.name
            return session_

    def get_session_id(self, session_name):
        with self.open_session() as session:
            session_ = session.query(Session).filter(Session.name == session_name).first()
            return session_.id

    def add_session(self, session_name):
        with self.open_session() as session:
            try:
                new_session = Session(name=session_name)
                session.add(new_session)
                session.flush()
                session.commit()
            except Exception as exc:
                session.rollback()

    def update_listing(self, listing_id, price, days_on_market):
        with self.open_session() as session:
            try:
                timestamp = generate_timestamp()

                smtp = update(Car).where(Car.listing_id == listing_id). \
                    values(current_price=price,
                           update_timestamp=timestamp,
                           updated=True,
                           days_on_market=days_on_market)
                session.execute(smtp)
                session.commit()
            except:
                session.rollback()

    def set_updated(self, listing_id):
        with self.open_session() as session:
            try:
                smtp = update(Url).where(Url.listing_id == listing_id). \
                    values(updated=True)
                session.execute(smtp)
                session.commit()
            except:
                session.rollback()

    def set_sold_status(self, listing_id, days_for_selling):
        timestamp = generate_timestamp()
        with self.open_session() as session:
            smtp = update(Car).where(Car.listing_id == listing_id). \
                values(status="Removed",
                       removed_timestamp=timestamp,
                       days_posted=abs(days_for_selling))
            session.execute(smtp)
            session.commit()

    def remove_listing(self, listing_id):
        with self.open_session() as session:
            smtp = delete(Car).where(Car.listing_id == listing_id)
            session.execute(smtp)
            session.commit()

    def get_grouped_listings(self):
        with self.open_session() as session:
            list_db = session.query(Car.id, Car.make, Car.model, Car.trim, Car.year, Car.km,
                                     Car.pc). \
                group_by(Car.make, Car.model, Car.trim, Car.year, Car.pc, Car.id, Car.km).all()

            # list_ = []
            # for db in list_db:
            #     list_.append({
            #         'id': db.id,
            #         'make': db.make,
            #         'model': db.model,
            #         'trim': db.trim,
            #         'year': db.year,
            #         'km': db.km,
            #         'pc':db.pc
            #     })
            return list_db

    def set_deal_quality(self, status, listing_id, price_difference):
        with self.open_session() as session:
            smtp = update(Car).where(Car.id == listing_id). \
                values(quality_deal=str(status),
                       price_difference=price_difference)
            session.execute(smtp)
            session.commit()

    def get_trim_list(self):
        trim_list = []
        with self.open_session() as session:
            trim_list_ = session.query(Car.trim, Car.make).distinct().all()
            for car in trim_list_:
                try:
                    trim = car[0]
                    make = car[1]
                except IndexError:
                    continue
                if trim is None:
                    continue
                trim_list.append(dict(trim=trim,
                                      make=make))

            return trim_list

    def update_days_on_market(self):
        timestamp = generate_timestamp()

        list_of_listings = self.get_all_urls()
        with self.open_session() as session:

            for listing in list_of_listings:
                listing_id = listing['listing_id']
                print listing_id
                first_timestamp = listing['timestamp']
                time_dif = first_timestamp - datetime.strptime(timestamp,
                                                               "%Y.%m.%d:%H:%M:%S")
                time_dif = time_dif.days
                smtp = update(Car).where(Car.listing_id==listing_id).values(days_on_market=abs(time_dif))
                session.execute(smtp)
                session.commit()

    def get_all_cars_listings(self, country):
        listing_list = []
        with self.open_session() as session:
            cars_data = session.query(Car).filter(Car.country == country).all()
            for car in cars_data:
                listing_list.append(car.listing_id)
            return listing_list


    def reset_updates(self):
        with self.open_session() as session:
            smtp = update(Url). \
                values(updated=False)
            session.execute(smtp)
            session.commit()

    def insert_trim(self, data):
        with self.open_session() as session:
            make = data['marka']
            model = data['model']
            trim = data['trim']
            year = data['year']
            engine_volume = data['engine_volume']
            specs = data['specs']
            short_specs = data['short_specs']
            transmission = data['transmission']
            short_transmission = data['short_transmission']
            min_price = data['min_price']
            max_price = data['max_price']
            type = data['type']
            hash_code = data['hash_code']
            new_row = Trims(make=make,
                            model=model,
                            year=year,
                            trim=trim,
                            engine_volume=engine_volume,
                            specs=specs,
                            short_specs=short_specs,
                            transmission=transmission,
                            short_transmission=short_transmission,
                            min_price=min_price,
                            max_price=max_price,
                            type=type,
                            hash_code = hash_code
                          )
            try:
                session.add(new_row)
                session.commit()
            except Exception as exc:
                print exc
                session.rollback()


if __name__ == '__main__':
    pass
    print DatabaseManager().get_trim_list()
