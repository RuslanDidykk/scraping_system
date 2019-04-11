from database.DatabaseManager import DatabaseManager

class DealQualityManager:
    def __init__(self):
        self.db = DatabaseManager()


    def group_cars(self, object_list):
        grouped_list = [[]]
        temp_object = object_list[0]
        index = 0
        for object in object_list:
            if object[1:5] == temp_object[1:5]:
                grouped_list[index].append(object)
            else:
                index += 1
                temp_object = object
                grouped_list.append([])
                grouped_list[index].append(object)

        return grouped_list

    def calculate_middle_price(self, car_list):
        summ = 0
        errors = 0
        for car in car_list:
            try:
                price = int(car[5])
                summ += price
            except:
                errors += 1
        try:
            middle_price = summ/(len(car_list)-errors)
        except ZeroDivisionError:
            middle_price = 0

        return middle_price

    def dealRating(self, list_cars):
        result_km = 0
        result_price = 0
        summ_km = 0
        summ_price = 0

        for car in list_cars:
            summ_km += car[5]
            summ_price += car[6]

        average_km = (summ_km / len(list_cars))
        average_price = (summ_price / len(list_cars))
        print 'Average km: ', average_km
        print 'Average price: ', average_price

        average_km_degree = average_km / 20
        average_price_degree = average_price / 20

        for car in list_cars:
            id = car[0]
            different_km = average_km - car[5]
            different_price = average_price - car[6]
            try:
                result_km = int(different_km / average_km_degree)
            except ZeroDivisionError:
                result_km = 0
            try:
                result_price = int(different_price / average_price_degree)
            except ZeroDivisionError:
                result_price = 0
            status = str(result_km + result_price)
            self.db.set_deal_quality(status=status, listing_id=id, price_difference=different_price)


    def calculate_deal_quality(self, car_list):
        middle_price = self.calculate_middle_price(car_list)
        for car in car_list:
            difference = 0
            id = car[0]
            price = int(car[5])
            difference = middle_price - price
            print car, middle_price, difference
            if difference > 3000:
                self.db.set_deal_quality(status="Excellent", listing_id=id, price_difference=difference)
            elif difference > 1500:
                self.db.set_deal_quality(status="Good", listing_id=id, price_difference=difference)
            elif difference < -1500:
                self.db.set_deal_quality(status="Poor", listing_id=id, price_difference=difference)
            else:
                self.db.set_deal_quality(status="Fair", listing_id=id, price_difference=difference)



    def main(self, car_list):
        car_list = self.group_cars(car_list)
        for grouped_cars in car_list:
            self.dealRating(list(grouped_cars))




if __name__ == '__main__':

    db = DatabaseManager()

    object_list = db.get_grouped_listings()

    for i in DealQualityManager().group_cars(object_list):
        if len(i) < 100 and len(i)> 70:
            print i

    # for i in DealQualityManager().group_cars(object_list):
    #     if len(i) > 100:
    #         print i[0].km


                    # DealQualityManager().main(object_list)


