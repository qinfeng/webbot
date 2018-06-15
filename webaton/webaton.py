from selenium import webdriver ;
from collections import OrderedDict
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep 
import sys , argparse , os  


class Browser:

    def __init__(self , showWindow = False ):
        options = webdriver.ChromeOptions()
        if(showWindow):
            options.set_headless(headless=True) ; 

        driverfilename = "chrome_linux" if  os.name=='posix' else "chrome_windows.exe" if os.name=='nt' else "chrome_mac" ; 
        driverpath =  os.path.join(os.path.split(__file__)[0] , 'drivers{0}{1}'.format(os.path.sep , driverfilename))
        self.driver = webdriver.Chrome(executable_path=driverpath , chrome_options=options)
        self.Key = Keys ;
        self.errors = list() ; 

        [setattr(self , function  , getattr(self.driver , function) ) for function in ['add_cookie' ,'delete_all_cookies','delete_cookie' , 'execute_script' , 'execute_async_script' ,'fullscreen_window','get_cookie' ,'get_cookies','get_log','get_network_conditions','get_screenshot_as_base64' ,'get_screenshot_as_file','get_screenshot_as_png','get_window_position','get_window_rect','get_window_size','maximize_window','minimize_window','implicitly_wait','quit','refresh','save_screenshot','set_network_conditions','set_page_load_timeout','set_script_timeout','set_window_position','set_window_rect','start_client','start_session','stop_client','switch_to_alert']]

        self.close_current_tab = self.driver.close ; 


    def get_current_url(self): return self.driver.current_url ;
    def get_current_window_handle(self):return self.driver.current_window_handle
    def get_application_cache(self):return self.driver.application_cache
    def get_desired_capabilities(self):return self.driver.desired_capabilities
    def get_log_types(self):return self.driver.log_types
    def get_title(self):return self.driver.title
    def get_page_source(self):return self.driver.page_source

    def __find_element__(self , text , tag , classname , id , number ,css_selector , xpath , match_level): 
   
        self.element_to_score = OrderedDict()
        self.element_to_score_id_set = set();
        if(tag=='link'):tag = 'a' ; 

        def add_to_init_text_matches_score(text_matches_elements : list , score :int )->None:
            '''Extends a dictionary and maps it with the text_matched_element with the score'''

            for element in text_matches_elements:
                try:
                    if (not element.is_displayed) or (element.get_attribute('hidden')=='true') or (element.tag_name=='input' and element.get_attribute('type')=='hidden'):
                        continue ; 

                    # accessing id or class attribute of stale element("like that input tag which in is google.com page ") raises this exception
                    element_tag_name = element.tag_name 
                
                except exceptions.StaleElementReferenceException as E:
                    print(E) ; 
                    continue ; 


                if(element.id in self.element_to_score_id_set):
                    ''' No need to call the max method if the method call is ordered from most specific to least specific which naturally has the max score if the element is already present '''
                    self.element_to_score[element] = max(self.element_to_score[element] , score ) ; 

                else:
                    self.element_to_score[element] = score ; 
                    self.element_to_score_id_set.add(element.id)
        


        def element_fetch_helper(xpath , score ):
            add_to_init_text_matches_score( self.driver.find_elements_by_xpath(xpath) , score ) ;


        def find_input_element_for_label(elementlist , score):
            '''This method finds the input tag elements by taking in the label elements and assigns the score argument to the new found input elements and puts them in the  elemenet to score mapping '''

            for element in elementlist:
                if(not element.is_displayed):
                    continue ; 

                possible_input_id = element.get_attribute('for') ; 
                try : 
                    element_fetch_helper(("//body//input[@id='{}']".format(possible_input_id)) , score )

                    add_to_init_text_matches_score( element.find_elements_by_xpath("../input[contains(translate(@id , '{}' ,'{}' ) , '{}')]".format(text.upper() , text.lower() ,  text.lower())) , score - 5)                    

                    add_to_init_text_matches_score( element.find_elements_by_xpath("/./preceding::input") ,  score - 7)                    

                    element_fetch_helper(("//body//input[@name='{}']".format(possible_input_id)) , score-6 )

                    add_to_init_text_matches_score( element.find_elements_by_xpath("../input") , score - 10)                    
                    

                except exceptions.NoSuchElementException as E:
                    print("Exception : {}".format(E)) ;
                


        def handle_input_tag():
            if(text):
                for test_attr in ['@value' , '@placeholder' , '@aria-label']:
                    element_fetch_helper(("//body//input[{}='{}']".format(test_attr, text)) , score=45 )
                    element_fetch_helper(("//body//input[contains( {} , '{}')]".format(test_attr , text)) , score=37 )
                    element_fetch_helper(("//body//input[contains(translate( {} , '{}' , '{}' ) , '{}')]".format(test_attr ,  text.upper() , text.lower() , text.lower())) ,score=33) ; 


                find_input_element_for_label(self.driver.find_elements_by_xpath("//body//label[text()='{}']".format(text)) , score =45)

                find_input_element_for_label(self.driver.find_elements_by_xpath("//body//label[contains( text() , '{}')]".format(text)) , score=37 )

                find_input_element_for_label(self.driver.find_elements_by_xpath("//body//label[contains(translate( text() , '{}' , '{}' ) , '{}')]".format(text.upper() , text.lower() , text.lower())) ,score=33) ; 

            else:
                element_fetch_helper("//body//{}".format(tag) , score=40) ; 

        
        def handle_button_or_link_tag(tagvar):
            if(text):
                element_fetch_helper(("//body//{}[text()='{}']".format( tagvar , text)) , score=45)
                element_fetch_helper(("//body//{}//*[text()='{}']".format(tagvar , text)) , score=45)

                add_to_init_text_matches_score(self.driver.find_elements_by_link_text("{}".format(text)) , score=43 ) ;

                element_fetch_helper(("//body//{}[contains(text() , '{}')]".format(tagvar , text)) , score=37 )
                element_fetch_helper(("//body//{}//*[contains(text() , '{}')]".format(tagvar , text)) , score=37 )

                element_fetch_helper(("//body//{}[contains(translate(text() , '{}' , '{}' ) , '{}')]".format(tagvar , text.upper() , text.lower() , text.lower())) ,score=33) ; 
                element_fetch_helper(("//body//{}//*[contains(translate(text() , '{}' , '{}' ) , '{}')]".format(tagvar , text.upper() , text.lower() , text.lower())) ,score=33);


            else:
                element_fetch_helper(("//body//{}".format(tagvar)) , score=40)




        def handle_loose_check():
            '''This method must only be used iff no element based on the given text input is found ! '''
            if(match_level=='loose' and text):
                element_fetch_helper("//body//*[@value='{}']".format(text) , score=30 ) ;
                element_fetch_helper("//body//*[text()='{}']".format(text) , score=30 ) ;

                element_fetch_helper(("//body//*[contains(text() , '{}')]".format(text)) , score=27 )

                element_fetch_helper(("//body//*[contains(translate(text() , '{}' , '{}' ) , '{}' )]".format(text.upper() , text.lower() , text.lower())) ,score=25) ; 


        if not text and tag:
            element_fetch_helper(("//body//{}".format(tag )) , score=50 )


        elif tag:
            element_fetch_helper(("//body//{}[@value='{}']".format(tag , text)) , score=50 )
            element_fetch_helper(("//body//{}[text()='{}']".format(tag , text)) , score=50 )
            element_fetch_helper(("//body//{}[contains(text() , '{}') ]".format(tag , text)) , score=49 )
            element_fetch_helper(("//body//{0}[contains(translate(text()  ,'{1}', '{2}') , '{2}') ]".format(tag , text.upper() , text.lower())) , score=48 )


        if(text.lower() in 'your password'):
            element_fetch_helper("//body//input[contains(@name , '{}') ]".format('password') , score=47)


        if(text.lower() in ['username' , 'email' , 'login'] and tag=='input'):
            element_fetch_helper('''//body//input[contains(translate(@name , 'USERNAME' , 'username' )  , 'username') or contains(translate(@name ,'EMAIL' , 'email' ) , 'email') or contains(translate(@name , 'LOGIN' , 'login'  ) , 'login' ) or contains(translate(@type , 'EMAIL' , 'email') , 'email')] ''' , 53 )



        if(tag=='input'):
            handle_input_tag()
            

        if(tag=='button'):
            handle_button_or_link_tag(tag)

            if(len(self.element_to_score.keys())==0):
                handle_input_tag() 
            if(len(self.element_to_score.keys())==0):
                handle_button_or_link_tag('a') 


        if(id):
            add_to_init_text_matches_score( self.driver.find_elements_by_id(id) , 100)
        if(classname):
            add_to_init_text_matches_score( self.driver.find_elements_by_class_name(classname) , 50 )



        if(not len(self.element_to_score.keys())):
            handle_loose_check()


        if(not len(self.element_to_score.keys())):
            print("No element found ! ") ; 
            return []; 


        for element in self.element_to_score.keys():
            score = self.element_to_score.get(element) ; 

            # Check ID
            if(id and id==element.get_attribute('id')):
                score += 100

            #Check Class
            if(classname and classname in element.get_attribute('class').split()):
                score+=50

            #Check element tag and check for button or anchor  or input or textarea
            if(tag.lower() in ["button",'link'] and element.tag_name in ['button' , 'a'] or (tag.lower()=='input' and 'input' == element.tag_name) ):
                score+=35
            
            # If user doesn't enter any tag [stick to default i.e button for click and input for type method ]
            if(tag in ['button' , 'input'] and element.tag_name in ['button' , 'a' , 'input'] ):
                score+=30

            self.element_to_score[element] = score; 
        
        max_score = max(self.element_to_score.values())
        max_scored_elements = [element for element in self.element_to_score.keys() if (self.element_to_score[element]==max_score)]

        self._max_score_elements_ = max_scored_elements 
        self._max_score_ = max_score

        print("\n\nMax SCORES " , max_scored_elements) ; 
        return (self._max_score_elements_ ) ; 



    def __set_error__(self , Exceptionerror , element = None  , message = ''):
        self.errors.append({Exceptionerror : Exceptionerror , element : element , message : message}) ; 
    

    def __reset_error__(self , error):
        self.errors = list() ; 


    def get_total_tabs(self):
        return len(self.driver.window_handles) ; 


    def switch_to_tab(self , number):
        assert number<=len(self.driver.window_handles) and number>0 , "Tab number must be less than or equal to the total number of tabs" ; 

        self.driver.switch_to_window(self.driver.window_handles[number-1]) ;
        

    def go_back(self):
        self.driver.back() ;

    def go_forward(self):
        self.driver.forward() ; 

    def go_to(self , url):
        self.driver.get(url) 


    def click(self , text='' , tag='button', id ='' , classname ='',  number = 1 , css_selector='' , xpath='' , match_level = 'loose'):

        if(not (text or id or classname or css_selector or xpath )):
            ActionChains(self.driver).click().perform()
            return ;


        maxElements = self.__find_element__(text , tag , classname , id , number , css_selector , xpath , match_level)

        for element in maxElements:
            try:
                element.click() ; 
                break ; 

            except Exception as E:
                self.__set_error__(E , element  , ''' tagname : {} , id : {}  , classname : {} , id_attribute : {}
                '''.format( element.tag_name , element.id , element.get_attribute('class') , element.get_attribute('id')) ) ; 

                print("Exception raised for the element : " ,'''
                tagname : {} , id : {}  , classname : {} , id_attribute : {}
                '''.format( element.tag_name , element.id , element.get_attribute('class') , element.get_attribute('id')) )
                print("Exception : \n\n" , E) ; 


    def scrolly(self , amount : int ):
        assert isinstance(amount , int) 
        self.driver.execute_script("window.scrollBy(0, {});".format(amount) ) ;


    def scrollx(self , amount : int ):
        assert isinstance(amount , int) 
        self.driver.execute_script("window.scrollBy( {}, 0 );".format(amount) ) ;
    

    def press(self , key):
        specialkeys = [key for key in dir(Keys) if '_' not in key]
        action = ActionChains(self.driver).key_down(key[0]) ; 
        for c in key[1:]:
            action = (action.key_down(c) if c in specialkeys else action.send_keys(c)) ; 

        action.key_up(Keys.CONTROL).key_up(Keys.ALT).key_up(Keys.SHIFT).key_up(Keys.COMMAND).key_up(Keys.LEFT_SHIFT).key_up(Keys.LEFT_CONTROL).key_up(Keys.LEFT_ALT).perform() ; 

   

    def type(self , text , into ='' , clear = True , tag='input', id ='' , classname ='',  number = 1 , css_selector='' , xpath='' , match_level = 'loose' ):
        if(not (into or id or classname or css_selector or xpath)):
            ActionChains(self.driver).send_keys(text).perform() ;
            return ;  

        maxElements = self.__find_element__(into , tag , classname , id , number , css_selector , xpath , match_level)

        for element in maxElements:
            try:
                if(clear):
                    element.clear() 
                element.send_keys(text)
                break ; 
 
            except exceptions.WebDriverException as E:
                print("Exception raised for the element : " ,'''
                tagname : {} , id : {}  , classname : {} , id_attribute : {}
                '''.format( element.tag_name , element.id , element.get_attribute('class') , element.get_attribute('id')) )
                print("Exception : \n\n" , E) ; 


    def select_tab(self , number):
        self.driver.find_element_by_css_selector("body").send_keys(Keys.CONTROL + 2);




class Chrome:
    pass


if(__name__=='__main__'):
    aton = Browser() ; 
    # aton.go_to('http://daedalcrafters.pythonanywhere.com') 
    aton.go_to('https://daedalcrafters.pythonanywhere.com')
    aton.type("akshay" , 'Username')
    aton.type("amazonmws" , 'Password')
    aton.click('LOGIN')
    aton.click('COPY') ; 