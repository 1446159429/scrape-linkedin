# -*- coding: utf-8 -*-
"""
@author: efourrier

Purpose : Create a unofficial api to get linkedin employment info with
http request and DOM parsing.

Notes :

"""

#########################################################
# Import package, helpers and constant
#########################################################

# Packages

from utils import CustomRequest

import random
import json
import pickle
import time

import requests
import lxml
from lxml import html
from requests import Request, Session



# Helpers

def extract_one(l, value = None):
	""" extract first value if len(l) == 1, value if 0 and return list otherwise """
	if len(l) == 0:
		return value
	else:
		return l[0]


def clean(l):
	if isinstance(l,list):
	    if l == []:
	        return []
	    else:
	        l = ([unicode(x).strip().replace(u'\t',u"") for x in l])
	        l =  [x for x in l if x != u""]
	        l =  [x for x in l if x != u',']
	        return l
	elif isinstance(l,str) or isinstance(l,unicode):
		return l.strip()
	elif isinstance(l,float) or isinstance(l,int):
		return l
	else:
		return l

def get_first_n(l):
    if l  == []:
        return 'error'
    else:
        return l[0]

# Constants

# proxy = {"http": "http://123proxysites.science",
#         "https" : "https://www.proxery.com"}

# get = partial(requests.get, headers={'user-agent': random.choice(list_user_agent)},allow_redirects=True)


# gd_url = 'http://www.glassdoor.com'
# url_api_glassdoor = 'http://www.glassdoor.com/api/employer/'


#########################################################
# MySession class
#########################################################


class LinkedinItem(object):

	attributes_key = [u'volunteerings',u'last_name',u'number_recommendations',u'number_connections',u'current_location',u'honors',u'first_name',u'current_title',u'test_scores',u'current_industry',u'languages',u'similar_profiles',u'interests',u'profile_img_url',u'current_education',u'educations',u'experiences',u'groups',u'organizations',u'certifications',u'name',u'skills',u'websites',u'summary',u'project',u'courses',u'publications',u'recommendations']

	def __init__(self,url = None,html_string = None,crequest=None):
		# if you want put the html text directly
		self.url = url
		self.html_string = html_string
		if self.html_string is not None:
			self.tree = html.fromstring(self.html_string)
		# otherwise request the url
		elif self.html_string is None and self.url is not None:
			self.crequest = CustomRequest() if crequest is None else crequest
			self.response = self.crequest.get(self.url)
			self.tree = html.fromstring(self.response.text)
		else:
			raise ValueError('url or html_string should be defined')
		# Header path
		self.xp_header = extract_one(self.tree.xpath('.//div[@class = "profile-card vcard"]'))
		# Experiences path
		self.xp_experiences = extract_one(self.tree.xpath('//div[@id = "background-experience"]'))
		# Projets
		self.xp_projects = extract_one(self.tree.xpath('//div[@id = "background-projects"]'))
		# Language
		self.xp_languages = extract_one(self.tree.xpath('//div[@id = "background-languages"]'))
		# Volunteering
		self.xp_volunteerings = extract_one(self.tree.xpath('//div[@id = "background-volunteering"]'))
		# Organizations
		self.xp_organizations = extract_one(self.tree.xpath('//div[@id = "background-organizations"]'))
		# Honors
		self.xp_honors = extract_one(self.tree.xpath('//div[@id = "background-honors"]'))
		# Test Scores
		self.xp_test_scores = extract_one(self.tree.xpath('//div[@id = "background-test-scores"]'))
		# Publications
		self.xp_publications = extract_one(self.tree.xpath('//div[@id = "background-publications"]'))
		# Education
		self.xp_educations = extract_one(self.tree.xpath('//div[@id = "background-education"]'))
		# Certifications
		self.xp_certifications = extract_one(self.tree.xpath('//div[@id = "background-certifications"]'))
		# Courses
		self.xp_courses = extract_one(self.tree.xpath('//div[@id = "courses"]'))
		# Similar profiles
		self.xp_similar_profiles = extract_one(self.tree.xpath('//div[@class = "insights-browse-map"]'))
		# Summary
		# self.xp_summary = extract_one(self.tree.xpath('//div[@id = "background-summary"]'))
		# Recommendation
		# self.xp_recommendations = extract_one(self.tree.xpath('//div[@id = "recommendations"]'))
		# Interests
		# self.interests = extract_one(self.tree.xpath('//div[@id = "background-interests"]'))
		# Skills
		# self.xp_skills = extract_one(self.tree.xpath('//div[@id = "background-skills"]'))

	@staticmethod
	def get_xp(origin,path):
		""" Helper to query xpath from origin """
		return clean(origin.xpath(path))


	def get_clean_xpath(self,x):
		return clean(self.tree.xpath(x))

	# Header

	def get_profile_img_url(self):
		return extract_one(self.get_xp(self.xp_header,'.//div[@class="profile-picture"]//img/@src'))

	def get_name(self):
		""" Return name of the profile """
		return extract_one(self.get_xp(self.xp_header,'.//span[@class="full-name"]/text()'))


	def get_first_name(self):
		""" Return first name """
		name = self.get_name()
		list_n = name.split() if name is not None else []
		return list_n[0] if len(list_n) == 2 else None

	def get_last_name(self):
		""" Return last name of the profile """
		name = self.get_name()
		list_n = name.split() if name is not None else []
		return list_n[1] if len(list_n) == 2 else None

	def get_current_title(self):
		""" Return current title """
		return extract_one(self.get_xp(self.xp_header,'.//*[@id="headline"]/p/text()'))

	def get_current_location(self):
		""" Return current location """
		return extract_one(self.get_xp(self.xp_header,'.//dd/span/text()'))

	def get_current_industry(self):
		""" Return current industry """
		return extract_one(self.get_xp(self.xp_header,'.//dd[@class="industry"]/text()'))

	def get_current_education(self):
		""" Return current education """
		name = extract_one(self.get_xp(self.xp_header,'.//tr[@id="overview-summary-education"]//li//text()'))
		url = extract_one(self.get_xp(self.xp_header,'.//tr[@id="overview-summary-education"]//li/a/@href'))
		return {u'name':name, u'url':url}

	def get_websites(self):
		""" Return a list of websites of the linkedin member """
		return self.get_xp(self.xp_header,'.//tr[@id="overview-summary-websites"]//li/a/@href')

	def get_number_connections(self):
		""" Return the number of connections """
		return extract_one(self.get_xp(self.xp_header,'.//div[@class = "member-connections"]//strong//text()'))

	def get_number_recommendations(self):
		""" Return the number of recommendations """
		return extract_one(self.get_clean_xpath('.//tr[@id = "overview-recommendation-count"]/td/ol/li/strong[1]/text()'))

	# Interests, Groups  Skills  and Languages
	def get_interests(self):
		""" Return a list of Interests """
		return self.get_clean_xpath('//ul[@class="interests-listing"]/li//text()')

	def get_groups(self):
		""" Return a dictionnary of the groups with different parameters (name,img,url) """
		names = self.get_clean_xpath('//p[@class="groups-name"]/a/img/@alt')
		imgs = self.get_clean_xpath('//p[@class="groups-name"]/a/img/@src')
		urls = self.get_clean_xpath('//p[@class="groups-name"]/a[1]/@href')
		return [{u'name': n, u'img': img, u'url': 'http://www.linkedin.com'+url} for n,img,url in zip(names,imgs,urls)]

	def get_skills(self):
		""" Return a list of skills """
		#url_skills = self.get_xp(self.skills,'.//span[@class="endorse-item-name-text"]/@href')
		# [{k:v} for k,v in zip(url_skills,name_skills)]
		name_skills = self.get_clean_xpath('//div[@id = "profile-skills"]//li//span[@class = "skill-pill"]//text()')
		return name_skills

	def get_languages(self):
		""" Return a list of dictionnary of languages with proficiency """
		if isinstance(self.xp_languages,html.HtmlElement) is True:
			languages_name = self.get_xp(self.xp_languages,'.//li/h4//text()')
			languages_proficiency = self.get_xp(self.xp_languages,'.//li/div//text()')
			return [{u'language':l,u'proficiency':p } for l,p in zip(languages_name,languages_proficiency)]
		else:
			return {}

	def get_summary(self):
		""" Return the summary of the linkedin profile """
		return ' '.join(self.get_clean_xpath('//div[@id = "background-summary"]//div[@class = "summary"]/p//text()'))

	def get_recommendations(self):
		""" Return a list of description of the recommendations """
		return self.get_clean_xpath('//div[@id = "recommendations"]//ul/li/div[@class = "description"]/text()')

	def get_volunteering_opportunities(self):
		""" Return a list of the volunteering causes the linkedin member is looking for """
		return self.get_clean_xpath('//div[@class="opportunities"]/ul[@class="volunteering-opportunities"]/li/text()')

	def get_volunteering_causes(self):
		""" Return a list of the volunteering causes the linkedin member cares bout """
		return self.get_clean_xpath('//div[@id="volunteering-causes-view"]//ul[@class="volunteering-listing"]/li/text()')

	def get_experiences(self):
		""" Return a list of dictionnary with experience details """
		if isinstance(self.xp_experiences,html.HtmlElement) is True:
			nb_experiences = int(self.get_clean_xpath('count(//div[@id="background-experience"]/div[contains(@id, "experience-")])'))
			experiences = []
			for i in range(1, nb_experiences+1):
				data = {}
				data[u'jobtitle'] = extract_one(self.get_xp(self.xp_experiences,'./div[%s]/div//h4//text()' % i))
				data[u'linkedin_jobtitle_url'] = extract_one(self.get_xp(self.xp_experiences,'./div[%s]/div//h4/a/@href' % i))
				data[u'company'] = extract_one(self.get_xp(self.xp_experiences,'./div[%s]/div//h5[2]/a/text()' % i))
				data[u'linkedin_company_url'] = extract_one(self.get_xp(self.xp_experiences,'./div[%s]/div//h5[2]/a/@href' % i))
				data[u'linkedin_company_img_url'] = extract_one(self.get_xp(self.xp_experiences,'./div[%s]/div//img/@src' % i))
				data[u'area'] = extract_one(self.get_xp(self.xp_experiences,'./div[%s]/div//span[@class="locality"]/text()' % i))
				data[u'description'] = ' '.join(self.get_xp(self.xp_experiences,'./div[%s]//p[contains(@class,"description")]/text()' % i))
				start_date = self.get_xp(self.xp_experiences,'./div[%s]/div//span[@class="experience-date-locale"]/time[1]/text()' % i)
				end_date = self.get_xp(self.xp_experiences,'./div[%s]/div//span[@class="experience-date-locale"]/time[2]/text()' % i)
				data[u'start_date'] = extract_one(start_date)
				if end_date:
					data[u'end_date'] = extract_one(end_date)
				else:
					data[u'end_date'] = unicode(time.strftime("%B-%Y"))
				experiences.append(data)
		else:
			experiences = []
		return experiences

	def get_educations(self):
		"""
		Return a list of dictionnary with education details
		"""
		if isinstance(self.xp_educations,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@id="background-education"]/div[contains(@id, "education-")])'))
			schools = []
			for i in range(1, count+1):
				data = {}
				data[u'degree'] = extract_one(self.get_xp(self.xp_educations,
					'./div[%s]//span[@class="degree"]//text()' % i))
				data[u'major'] = extract_one(self.get_xp(self.xp_educations,
					'./div[%s]//span[@class="major"]//text()' % i))
				data[u'university_name'] = extract_one(self.get_xp(self.xp_educations,
					'./div[%s]//h4//text()' % i))
				data[u'linkedin_university_url'] = extract_one(self.get_xp(self.xp_educations,
					'./div[%s]/div//h4/a/@href' % i))
				data[u'linkedin_university_img_url'] = extract_one(self.get_xp(self.xp_educations,
					'./div[%s]/div//img/@src' % i))
				data[u'description'] = ' '.join(self.get_xp(self.xp_educations,'./div[%s]//p[contains(@class,"notes")]/text()' % i))
				start_date = self.get_xp(self.xp_educations,'./div[%s]//span[@class="education-date"]/time[1]/text()' % i)
				end_date = self.get_xp(self.xp_educations,'./div[%s]//span[@class="education-date"]/time[2]/text()' % i)
				data[u'start_date'] = extract_one(start_date)
				if end_date:
					data[u'end_date'] = extract_one(end_date)
				else:
					data[u'end_date'] = unicode(time.strftime("%B-%Y"))
				schools.append(data)
		else:
			schools = []

		return schools

	def get_projects(self):
		""" Return a list of dictionnary with project details """
		if isinstance(self.xp_projects,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@id="background-projects"]/div[contains(@id, "project-")])'))
			projects = []
			for i in range(1, count+1):
				data = {}
				data[u'title'] = extract_one(self.get_xp(self.xp_projects,'./div[%s]//h4//span[1]/text()' % i))
				data[u'url'] = extract_one(self.get_xp(self.xp_projects,'./div[%s]//h4/a/@href' % i))
				data[u'description'] = ' '.join(self.get_xp(self.xp_projects,'./div[%s]//p[contains(@class,"description")]//text()' % i))
				data['team_members'] = self.get_xp(self.xp_projects,'./div[%s]//dd[@class="associated-endorsements"]//li/a/text()' % i)
				data['team_members_url'] = self.get_xp(self.xp_projects,'./div[%s]//dd[@class="associated-endorsements"]//li/a/@href' % i)
				# data[u'team_members'] = [{'name': n, 'url': url} for n,url in zip(team_members,team_members_url)]
				start_date = self.get_xp(self.xp_projects,'./div[%s]/div//span[@class="projects-date"]/time[1]/text()' % i)
				end_date = self.get_xp(self.xp_projects,'./div[%s]/div//span[@class="projects-date"]/time[2]/text()' % i)
				data[u'start_date'] = extract_one(start_date)
				if end_date:
					data[u'end_date'] = extract_one(end_date)
				else:
					data[u'end_date'] = unicode(time.strftime("%B-%Y"))
				projects.append(data)
		else:
			return []
		return projects


	def get_courses(self):
		""" Return a list of dictionnary with courses details """
		if isinstance(self.xp_courses,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@id="background-courses"]//div[@class="section-item"])'))
			courses = []
			for i in range(1, count+1):
				data = {}
				data[u'university'] = extract_one(self.get_xp(self.xp_courses,'.//div[@id="courses-view"]/div[%s]//h4/a/text()' % i))
				data[u'university_url'] = extract_one(self.get_xp(self.xp_courses,'.//div[@id="courses-view"]/div[%s]//h4/a/@href' % i))
				data[u'courses_name'] = extract_one(self.get_xp(self.xp_courses,'.//div[@id="courses-view"]/div[%s]//li/text()' % i))
				data[u'courses_number'] = extract_one(self.get_xp(self.xp_courses,'.//div[@id="courses-view"]/div[%s]//li/span/text()' % i))
				courses.append(data)
		else:
			courses = []
		return courses

	def get_honors(self):
		""" Return a list of dictionnary with honors and awards details """
		if isinstance(self.xp_honors,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@id="background-honors"]/div[contains(@id, "honors-")])'))
			honors = []
			for i in range(1, count+1):
				data = {}
				data[u'title'] = extract_one(self.get_xp(self.xp_honors,'./div[%s]//h4//text()' % i))
				data[u'delivred_by'] = extract_one(self.get_xp(self.xp_honors,'./div[%s]//h5//text()' % i))
				data[u'description'] = ' '.join((self.get_xp(self.xp_honors,'./div[%s]//p[contains(@class,"description")]//text()' % i)))
				data[u'date'] = extract_one(self.get_xp(self.xp_honors,'./div[%s]//span[@class = "honor-date"]/time/text()' % i))
				honors.append(data)
		else:
			honors = []
		return honors

	def get_volunteerings(self):
		""" Return a list of dictionnary with volunteering experiences """
		if isinstance(self.xp_volunteerings,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@id="background-volunteering"]//div[@class = "experience"])'))
			volunteerings = []
			for i in range(1, count+1):
				data = {}
				data[u'title'] = extract_one(self.get_xp(self.xp_volunteerings,'./div[%s]//h4//text()' % i))
				data[u'company'] = extract_one(self.get_xp(self.xp_volunteerings,'./div[%s]//h5//text()' % i))
				data[u'company_url'] = extract_one(self.get_xp(self.xp_volunteerings,'./div[%s]//h5//@href' % i))
				data[u'description'] = ' '.join((self.get_xp(self.xp_volunteerings,'./div[%s]//p[contains(@class,"description")]//text()' % i)))
				data[u'start_date'] = extract_one(self.get_xp(self.xp_volunteerings,'./div[%s]//span[@class = "volunteering-date-cause"]/time[1]/text()' % i))
				data[u'end_date'] = extract_one(self.get_xp(self.xp_volunteerings,'./div[%s]//span[@class = "volunteering-date-cause"]/time[2]/text()' % i))
				volunteerings.append(data)
		else:
			volunteerings = []
		return volunteerings

	def get_organizations(self):
		""" Return a list of dictionnary with organizations """
		if isinstance(self.xp_organizations,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@id="background-organizations"]/div[contains(@id, "organization-")])'))
			organizations = []
			for i in range(1, count+1):
				data = {}
				data[u'title'] = extract_one(self.get_xp(self.xp_organizations,'./div[%s]//h5//text()' % i))
				data[u'name'] = extract_one(self.get_xp(self.xp_organizations,'./div[%s]//h4//text()' % i))
				data[u'organization_url'] = extract_one(self.get_xp(self.xp_organizations,'./div[%s]//h5//@href' % i))
				data[u'description'] = ' '.join((self.get_xp(self.xp_organizations,'./div[%s]//p[contains(@class,"description")]//text()' % i)))
				data[u'start_date'] = extract_one(self.get_xp(self.xp_organizations,'./div[%s]//span[@class = "organizations-date"]/time[1]/text()' % i))
				data[u'end_date'] = extract_one(self.get_xp(self.xp_organizations,'./div[%s]//span[@class = "organizations-date"]/time[2]/text()' % i))
				organizations.append(data)
		else:
			organizations = []
		return organizations

	def get_test_scores(self):
		""" Return a list of dictionnary with test scores """
		if isinstance(self.xp_test_scores,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@id="background-test-scores"]/div[contains(@id, "scores-")])'))
			test_scores = []
			for i in range(1, count+1):
				data = {}
				data[u'name'] = extract_one(self.get_xp(self.xp_test_scores,'./div[%s]//h4//text()' % i))
				data[u'score'] = extract_one(self.get_xp(self.xp_test_scores,'./div[%s]//h5//text()' % i))
				data[u'description'] = ' '.join((self.get_xp(self.xp_test_scores,'./div[%s]//p[contains(@class,"description")]//text()' % i)))
				data[u'date'] = extract_one(self.get_xp(self.xp_test_scores,'./div[%s]//span[@class = "test-scores-date"]/time[1]/text()' % i))
				test_scores.append(data)
		else:
			test_scores = []
		return test_scores

	def get_certifications(self):
		""" Return a list of dictionnary with certifications infos """
		if isinstance(self.xp_certifications,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@id="background-certifications"]/div[contains(@id, "certification-")])'))
			certifications = []
			for i in range(1, count+1):
				data = {}
				data[u'title'] = extract_one(self.get_xp(self.xp_certifications,'./div[%s]//h4/a/text()' % i))
				data[u'title_url'] = extract_one(self.get_xp(self.xp_certifications,'./div[%s]//h4/a/@href' % i))
				data[u'company_name'] = extract_one(self.get_xp(self.xp_certifications,'./div[%s]//h5/a/text()' % i))
				data[u'linkedin_company_url'] = extract_one(self.get_xp(self.xp_certifications,'./div[%s]//h5//@href' % i))
				data[u'date'] = extract_one(self.get_xp(self.xp_certifications,'./div[%s]//span[@class = "certification-date"]/time/text()' % i))
				certifications.append(data)
		else:
			certifications = []
		return certifications

	def get_publications(self):
		""" Return a list of dictionnary with publications details """
		if isinstance(self.xp_publications,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@id="background-publications"]/div[contains(@id, "publication-")])'))
			publications = []
			for i in range(1, count+1):
				data = {}
				data[u'title'] = extract_one(self.get_xp(self.xp_publications,'./div[%s]//h4//span[1]/text()' % i))
				data[u'title_url'] = extract_one(self.get_xp(self.xp_publications,'./div[%s]//h4//@href' % i))
				data[u'source'] = extract_one(self.get_xp(self.xp_publications,'./div[%s]//h5//text()' % i))
				data[u'description'] = ' '.join((self.get_xp(self.xp_publications,'./div[%s]//p[contains(@class,"description")]//text()' % i)))
				data[u'date'] = extract_one(self.get_xp(self.xp_publications,'./div[%s]//span[@class = "publication-date"]//text()' % i))
				data[u'authors'] = extract_one(self.get_xp(self.xp_publications,'./div[%s]//dd[@class = "associated-endorsements"]//li//text()' % i))
				data[u'authors_linkedin_profile'] = extract_one(self.get_xp(self.xp_publications,'./div[%s]//dd[@class = "associated-endorsements"]//li//@href' % i))
				publications.append(data)
		else:
			publications = []
		return publications

	def get_similar_profiles(self):
		""" Get a list of dictionnaries of profiles from 'people also viewed' on linkedin """
		if isinstance(self.xp_similar_profiles,html.HtmlElement) is True:
			count = int(self.get_clean_xpath('count(//div[@class="insights-browse-map"]/ul/li)'))
			similar_profiles = []
			for i in range(1, count+1):
				data = {}
				data[u'linkedin_url'] = extract_one(self.get_xp(self.xp_similar_profiles,'.//li[%s]/h4/a/@href' % i))
				data[u'name'] = extract_one(self.get_xp(self.xp_similar_profiles,'.//li[%s]/h4/a/text()' % i))
				data[u'current_title'] = extract_one(self.get_xp(self.xp_similar_profiles,'.//li[%s]/p/text()' % i))
				data[u'likedin_img_url'] = extract_one(self.get_xp(self.xp_similar_profiles,'.//li[%s]//a/img/@data-li-src' % i))
				similar_profiles.append(data)
		else:
			similar_profiles = []
		return similar_profiles



	def to_dict(self):
		data = {
		u'name': self.get_name(),
		u'first_name': self.get_first_name(),
		u'last_name': self.get_last_name(),
		u'number_connections':self.get_number_connections(),
		u'number_recommendations':self.get_number_recommendations(),
		u'websites':self.get_websites(),
		u'profile_img_url': self.get_profile_img_url(),
		u'current_education' : self.get_current_education(),
		u'current_title': self.get_current_title(),
		u'current_location': self.get_current_location(),
		u'current_industry': self.get_current_industry(),
		u'summary': self.get_summary(),
		u'recommendations': self.get_recommendations(),
		u'experiences': self.get_experiences(),
		u'educations': self.get_educations(),
		u'project': self.get_projects(),
		u'skills': self.get_skills(),
		u'courses': self.get_courses(),
		u'interests': self.get_interests(),
		u'groups': self.get_groups(),
		u'languages' : self.get_languages(),
		u'honors' : self.get_honors(),
		u'volunteerings': self.get_volunteerings(),
		u'organizations' : self.get_organizations(),
		u'test_scores' : self.get_test_scores(),
		u'certifications':self.get_certifications(),
		u'publications':self.get_publications(),
		u'similar_profiles' : self.get_similar_profiles()
		}
		return data







