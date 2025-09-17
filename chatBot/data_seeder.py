from typing import List
from model import FAQ
from database import db
import logging

logger = logging.getLogger(__name__)

class DataSeeder:
    @staticmethod
    async def seed_sample_faqs():
        """Seed database with sample FAQ data"""
        
        sample_faqs = [
            # Admissions
            {
                "question": "What are the admission requirements?",
                "answer": "Admission requirements vary by program. Generally, you need to have completed 12th grade with minimum 60% marks, pass our entrance exam, and submit required documents including academic transcripts, ID proof, and passport photos.",
                "keywords": ["admission", "requirements", "eligibility", "entrance", "12th", "marks"],
                "category": "admissions",
                "languages": {
                    "hi": {
                        "question": "प्रवेश की आवश्यकताएं क्या हैं?",
                        "answer": "प्रवेश की आवश्यकताएं कार्यक्रम के अनुसार अलग-अलग होती हैं। आमतौर पर, आपको न्यूनतम 60% अंकों के साथ 12वीं कक्षा पूरी करनी होगी, हमारी प्रवेश परीक्षा पास करनी होगी, और शैक्षणिक प्रतिलेख, पहचान प्रमाण, और पासपोर्ट फोटो सहित आवश्यक दस्तावेज जमा करने होंगे।"
                    },
                    "ta": {
                        "question": "சேர்க்கை தேவைகள் என்ன?",
                        "answer": "சேர்க்கை தேவைகள் திட்டத்தின் அடிப்படையில் மாறுபடும். பொதுவாக, நீங்கள் குறைந்தம் 60% மதிப்பெண்களுடன் 12வது வகுப்பை முடித்திருக்க வேண்டும், எங்கள் நுழைவுத் தேர்வில் தேர்ச்சி பெற வேண்டும், மற்றும் கல்வி ஆவணங்கள், அடையாள சான்று மற்றும் பாஸ்போர்ட் புகைப்படங்கள் உட்பட தேவையான ஆவணங்களை சமர்ப்பிக்க வேண்டும்."
                    }
                }
            },
            
            # Fees
            {
                "question": "What are the tuition fees for different courses?",
                "answer": "Tuition fees vary by program: Engineering courses: ₹80,000-120,000 per year, Management courses: ₹60,000-90,000 per year, Arts/Science: ₹30,000-50,000 per year. Additional fees include laboratory, library, and examination fees.",
                "keywords": ["fees", "tuition", "cost", "payment", "courses", "engineering", "management"],
                "category": "fees",
                "languages": {
                    "hi": {
                        "question": "विभिन्न पाठ्यक्रमों के लिए ट्यूशन फीस क्या है?",
                        "answer": "ट्यूशन फीस कार्यक्रम के अनुसार अलग होती है: इंजीनियरिंग पाठ्यक्रम: ₹80,000-120,000 प्रति वर्ष, प्रबंधन पाठ्यक्रम: ₹60,000-90,000 प्रति वर्ष, कला/विज्ञान: ₹30,000-50,000 प्रति वर्ष। अतिरिक्त शुल्क में प्रयोगशाला, पुस्तकालय और परीक्षा शुल्क शामिल हैं।"
                    },
                    "ta": {
                        "question": "வெவ்வேறு படிப்புகளுக்கான கல்விக் கட்டணம் என்ன?",
                        "answer": "கல்விக் கட்டணம் திட்டத்தின் அடிப்படையில் மாறுபடும்: பொறியியல் படிப்புகள்: ஆண்டுக்கு ₹80,000-120,000, மேலாண்மை படிப்புகள்: ஆண்டுக்கு ₹60,000-90,000, கலை/அறிவியல்: ஆண்டுக்கு ₹30,000-50,000। கூடுதல் கட்டணங்களில் ஆய்வகம், நூலகம் மற்றும் தேர்வு கட்டணங்கள் அடங்கும்."
                    }
                }
            },
            
            # Academics
            {
                "question": "When will the semester results be declared?",
                "answer": "Semester results are typically declared within 4-6 weeks after the examination ends. Results are published on the college website and students are notified via SMS and email. You can check results using your roll number and date of birth.",
                "keywords": ["results", "semester", "exam", "declaration", "marks", "grades"],
                "category": "academics",
                "languages": {
                    "hi": {
                        "question": "सेमेस्टर परिणाम कब घोषित होंगे?",
                        "answer": "सेमेस्टर परिणाम आमतौर पर परीक्षा समाप्त होने के 4-6 सप्ताह के भीतर घोषित होते हैं। परिणाम कॉलेज की वेबसाइट पर प्रकाशित किए जाते हैं और छात्रों को SMS और ईमेल के माध्यम से सूचित किया जाता है। आप अपने रोल नंबर और जन्म तिथि का उपयोग करके परिणाम देख सकते हैं।"
                    },
                    "ta": {
                        "question": "செமஸ்டர் முடிவுகள் எப்போது அறிவிக்கப்படும்?",
                        "answer": "செமஸ்டர் முடிவுகள் பொதுவாக தேர்வு முடிந்த 4-6 வாரங்களுக்குள் அறிவிக்கப்படும். முடிவுகள் கல்லூரி இணையதளத்தில் வெளியிடப்பட்டு, மாணவர்களுக்கு SMS மற்றும் மின்னஞ்சல் மூலம் தெரிவிக்கப்படும். உங்கள் ரோல் எண் மற்றும் பிறந்த தேதியைப் பயன்படுத்தி முடிவுகளைச் சரிபார்க்கலாம்."
                    }
                }
            },
            
            # Schedule
            {
                "question": "What is the class timetable for this semester?",
                "answer": "Class timetables are available on the college website under the 'Academics' section. Timetables are also posted on department notice boards. Classes typically run from 9:00 AM to 4:30 PM with lunch break from 12:30 PM to 1:30 PM.",
                "keywords": ["timetable", "schedule", "classes", "timing", "semester"],
                "category": "schedule",
                "languages": {
                    "hi": {
                        "question": "इस सेमेस्टर के लिए कक्षा समय सारणी क्या है?",
                        "answer": "कक्षा समय सारणी कॉलेज की वेबसाइट पर 'शिक्षाविद्' खंड के तहत उपलब्ध है। समय सारणी विभाग के नोटिस बोर्ड पर भी पोस्ट की जाती है। कक्षाएं आमतौर पर सुबह 9:00 बजे से शाम 4:30 बजे तक चलती हैं और दोपहर 12:30 बजे से 1:30 बजे तक लंच ब्रेक होता है।"
                    },
                    "ta": {
                        "question": "இந்த செமஸ்டருக்கான வகுப்பு நேர அட்டவணை என்ன?",
                        "answer": "வகுப்பு நேர அட்டவணைகள் கல்லூரி இணையதளத்தில் 'கல்வி' பிரிவின் கீழ் கிடைக்கின்றன. நேர அட்டவணைகள் துறை அறிவிப்பு பலகைகளிலும் வெளியிடப்படுகின்றன. வகுப்புகள் பொதுவாக காலை 9:00 மணி முதல் மாலை 4:30 மணி வரை நடக்கும், மதிய உணவு இடைவேளை மதியம் 12:30 முதல் 1:30 வரை."
                    }
                }
            },
            
            # Facilities
            {
                "question": "What facilities are available in the college library?",
                "answer": "The library offers: 50,000+ books, digital resources, 100 reading seats, air conditioning, Wi-Fi, photocopying services, and computer terminals. Library hours: 8:00 AM to 8:00 PM (Monday-Saturday), 10:00 AM to 6:00 PM (Sunday).",
                "keywords": ["library", "facilities", "books", "reading", "hours", "services"],
                "category": "facilities",
                "languages": {
                    "hi": {
                        "question": "कॉलेज पुस्तकालय में कौन सी सुविधाएं उपलब्ध हैं?",
                        "answer": "पुस्तकालय में शामिल है: 50,000+ पुस्तकें, डिजिटल संसाधन, 100 पठन सीटें, एयर कंडीशनिंग, Wi-Fi, फोटोकॉपी सेवाएं, और कंप्यूटर टर्मिनल। पुस्तकालय के समय: सुबह 8:00 बजे से रात 8:00 बजे (सोमवार-शनिवार), सुबह 10:00 बजे से शाम 6:00 बजे (रविवार)।"
                    },
                    "ta": {
                        "question": "கல்லூரி நூலகத்தில் என்ன வசதிகள் உள்ளன?",
                        "answer": "நூலகத்தில் உள்ளவை: 50,000+ புத்தகங்கள், டிஜிட்டல் ஆதாரங்கள், 100 படிக்கும் இடங்கள், ஏர் கண்டிஷனிங், Wi-Fi, புகைப்பட நகல் சேவைகள், மற்றும் கணினி முனையங்கள். நூலக நேரம்: காலை 8:00 முதல் இரவு 8:00 வரை (திங்கள்-சனி), காலை 10:00 முதல் மாலை 6:00 வரை (ஞாயிறு)."
                    }
                }
            },
            
            # Scholarships
            {
                "question": "What scholarships are available for students?",
                "answer": "Available scholarships include: Merit-based scholarships (up to 50% tuition waiver), Need-based financial aid, Government scholarships for SC/ST/OBC students, Sports scholarships, and Special scholarships for outstanding academic performance. Application deadlines vary by scholarship type.",
                "keywords": ["scholarship", "financial", "aid", "merit", "government", "sports"],
                "category": "fees",
                "languages": {
                    "hi": {
                        "question": "छात्रों के लिए कौन सी छात्रवृत्तियां उपलब्ध हैं?",
                        "answer": "उपलब्ध छात्रवृत्तियों में शामिल हैं: मेधा-आधारित छात्रवृत्ति (50% तक ट्यूशन छूट), आवश्यकता-आधारित वित्तीय सहायता, SC/ST/OBC छात्रों के लिए सरकारी छात्रवृत्ति, खेल छात्रवृत्ति, और उत्कृष्ट शैक्षणिक प्रदर्शन के लिए विशेष छात्रवृत्ति। आवेदन की अंतिम तिथि छात्रवृत्ति के प्रकार के अनुसार अलग होती है।"
                    },
                    "ta": {
                        "question": "மாணவர்களுக்கு என்ன உதவித்தொகைகள் கிடைக்கின்றன?",
                        "answer": "கிடைக்கும் உதவித்தொகைகள்: தகுதி அடிப்படையிலான உதவித்தொகை (50% வரை கல்விக் கட்டண விலக்கு), தேவை அடிப்படையிலான நிதி உதவி, SC/ST/OBC மாணவர்களுக்கான அரசு உதவித்தொகை, விளையாட்டு உதவித்தொகை, மற்றும் சிறந்த கல்வி செயல்பாட்டிற்கான சிறப்பு உதவித்தொகை. விண்ணப்ப கடைசி தேதி உதவித்தொகை வகையைப் பொறுத்து மாறுபடும்."
                    }
                }
            },
            
            # Placement
            {
                "question": "How is the placement record of the college?",
                "answer": "Our placement record is excellent with 85% placement rate. Top recruiters include TCS, Infosys, Wipro, Accenture, and many startups. Average package is ₹4.5 LPA with highest package reaching ₹12 LPA. We have dedicated placement cell and conduct regular training programs.",
                "keywords": ["placement", "job", "recruitment", "companies", "package", "career"],
                "category": "placement",
                "languages": {
                    "hi": {
                        "question": "कॉलेज का प्लेसमेंट रिकॉर्ड कैसा है?",
                        "answer": "हमारा प्लेसमेंट रिकॉर्ड 85% प्लेसमेंट दर के साथ उत्कृष्ट है। शीर्ष रिक्रूटर्स में TCS, Infosys, Wipro, Accenture, और कई स्टार्टअप शामिल हैं। औसत पैकेज ₹4.5 LPA है और सर्वोच्च पैकेज ₹12 LPA तक पहुंचा है। हमारे पास समर्पित प्लेसमेंट सेल है और नियमित प्रशिक्षण कार्यक्रम आयोजित करते हैं।"
                    },
                    "ta": {
                        "question": "கல்லூரியின் வேலைவாய்ப்பு பதிவு எப்படி இருக்கிறது?",
                        "answer": "எங்கள் வேலைவாய்ப்பு பதிவு 85% வேலைவாய்ப்பு விகிதத்துடன் சிறந்தது. முக்கிய ஆட்சேர்ப்பாளர்களில் TCS, Infosys, Wipro, Accenture மற்றும் பல தொடக்க நிறுவனங்கள் அடங்கும். சராசரி பேக்கேஜ் ₹4.5 LPA ஆகும், மற்றும் அதிகபட்ச பேக்கேஜ் ₹12 LPA வரை சென்றுள்ளது. எங்களிடம் பிரத்யேக வேலைவாய்ப்பு பிரிவு உள்ளது மற்றும் வழக்கமான பயிற்சி திட்டங்களை நடத்துகிறோம்."
                    }
                }
            }
        ]
