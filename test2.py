from olympedia_scraping import OlympediaScraper

# result_url = "https://www.olympedia.org/countries/USA/editions/59"
olympedia_scraping = OlympediaScraper()

# result = olympedia_scraping.get_bio_and_results_from_athlete_id("93860")
# result = olympedia_scraping.get_bio_and_results_from_athlete_id("17500")

result = olympedia_scraping.get_html_from_result_id('8772')
print(result)
