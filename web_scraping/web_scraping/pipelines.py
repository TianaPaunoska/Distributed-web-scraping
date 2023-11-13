# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        for field_name in field_names:
            value = adapter.get(field_name)

            if isinstance(value, tuple):
                new_values = []

                for v in value:
                    if isinstance(v, str):
                        new_values.append(v.strip())
                    else:
                        new_values.append(v)

                adapter[field_name] = tuple(new_values)
            elif isinstance(value, str):
                adapter[field_name] = value.strip()

        return item
    
class SaveToMySQLPipeline:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'root',
            database = 'books',
        )
        #cursor za izvrshuvanje na komandi
        self.cur = self.conn.cursor()
        #kreiranje na books table ako ne postoi
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id int NOT NULL auto_increment,
            url VARCHAR(255),
            title text,
            product_type VARCHAR(255),
            price_excl_tax DECIMAL,
            price_incl_tax DECIMAL,
            tax DECIMAL,
            price DECIMAL,
            availability INTEGER,
            num_reviews INTEGER,
            stars VARCHAR(255),
            category VARCHAR(255),
            description text,
            PRIMARY KEY (id)
        )
        """)
    def process_item(self, item, spider):
         # Convert tuple to string
        item = {key: value[0] if isinstance(value, tuple) else value for key, value in item.items()}
        # Remove currency symbol from price fields
        price_fields = ["price", "price_excl_tax", "price_incl_tax", "tax"]
        for field in price_fields:
            if field in item:
                item[field] = item[field].replace("£", "")
        availability = ''.join(filter(str.isdigit, item["availability"]))
        self.cur.execute(
            """INSERT INTO books (
                url,
                title,
                product_type,
                price_excl_tax,
                price_incl_tax,
                tax,
                price,
                availability,
                num_reviews,
                stars,
                category,
                description
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )""",
            (
                item["url"],
                item["title"],
                item["product_type"],
                item["price_excl_tax"],
                item["price_incl_tax"],
                item["tax"],
                item["price"],
                availability,
                item["num_reviews"],
                item["stars"],
                item["category"],
                item["description"]  
            )
        )
        #izvrshuvanje na insert
        self.conn.commit()
        return item   
    def close_spider(self, spider):
        #zatvoranje na cursor i konekcijata so bazata
        self.cur.close()
        self.conn.close()
        