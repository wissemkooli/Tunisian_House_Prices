import scrapy

class MubawabSpider(scrapy.Spider):
    name = "mubawab"
    allowed_domains = ["mubawab.tn"]
    start_urls = [
        "https://www.mubawab.tn/fr/cc/immobilier-a-vendre-all:sc:house-sale,villa-sale"
    ]

    def parse(self, response):
        self.logger.info(f"Visited main page: {response.url}")
        count = 0
        for box in response.css('div.listingBox'):
            count += 1
            listing_url = box.css('h2.listingTit a::attr(href)').get()
            if not listing_url:
                self.logger.debug(f"SKIP: No listing URL found for listingBox #{count}")
                continue
            listing_url = response.urljoin(listing_url)
            self.logger.info(f"Enqueue detail page #{count}: {listing_url}")
            yield scrapy.Request(
                listing_url,
                callback=self.parse_listing,
                meta={'url': listing_url, 'box_num': count}
            )
        self.logger.info(f"Processed {count} listingBox entries on main page.")

        # Pagination for more result pages
        current_url = response.url
        if ":p:" not in current_url:
            for page_num in range(2, 121):
                new_url = f"{current_url}:p:{page_num}"
                self.logger.info(f"Paginating to: {new_url}")
                yield scrapy.Request(new_url, callback=self.parse)

    def parse_listing(self, response):
        box_num = response.meta['box_num']
        url = response.meta['url']
        self.logger.info(f"Visited detail page #{box_num}: {url}")

        # Extract all fields from detail page
        title = response.css('h1.searchTitle::text').get() or response.css('h2.listingTit a::text').get()
        price = response.css('span.priceTag::text').get() or response.css('h3.orangeTit::text').get()
        location = response.css('span.listingH3 ::text').get() or response.css('h3.greyTit::text').get()
        location = location.strip() if location else None

        area, num_rooms, num_bedrooms, num_baths = None, None, None, None
        for feat in response.css('div.adDetailFeature span::text').getall():
            if "m²" in feat:
                area = feat.split()[0]
            elif "Pièce" in feat:
                num_rooms = feat.split()[0]
            elif "Chambre" in feat:
                num_bedrooms = feat.split()[0]
            elif "Salle de bains" in feat:
                num_baths = feat.split()[0]

        gen_fields = {
            'Type_de_bien': None,
            'Surface_de_la_parcelle': None,
            'Etat': None,
            'Annees': None,
            'Type_du_sol': None,
            'Nombre_detages': None,
        }
        for main_feat in response.css('div.adMainFeature'):
            label = main_feat.css('p.adMainFeatureContentLabel::text').get()
            value = main_feat.css('p.adMainFeatureContentValue::text').get()
            if label and value:
                field = label.strip().replace(" ", "_")
                if field in gen_fields:
                    gen_fields[field] = value.strip()
                self.logger.debug(f"Box {box_num} detail: {field} = {value.strip()}")

        features = [f.strip() for f in response.css('.adFeature span.fSize11::text').getall()]
        features_str = ";".join(features) if features else None

        lat = response.css('#mapOpen::attr(lat)').get()
        lon = response.css('#mapOpen::attr(lon)').get()

        item = {
            'title': title.strip() if title else None,
            'price': price.strip() if price else None,
            'location': location,
            'area': area,
            'num_rooms': num_rooms,
            'num_bedrooms': num_bedrooms,
            'num_baths': num_baths,
            'Type_de_bien': gen_fields['Type_de_bien'],
            'Surface_de_la_parcelle': gen_fields['Surface_de_la_parcelle'],
            'Etat': gen_fields['Etat'],
            'Annees': gen_fields['Annees'],
            'Type_du_sol': gen_fields['Type_du_sol'],
            'Nombre_detages': gen_fields['Nombre_detages'],
            'features': features_str,
            'latitude': lat,
            'longitude': lon,
            'url': url,
        }
        self.logger.info(f"Yielding box #{box_num} from detail page: {item}")
        yield item
