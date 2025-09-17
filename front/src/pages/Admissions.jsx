import React from 'react';
import { Calendar, Download, Mail, Phone, GraduationCap, Clock, Users } from 'lucide-react';

const Admissions = () => {
  const feeStructure = [
    { program: 'Bachelor of Engineering', duration: '4 Years', fee: '₹85,000', semester: '₹42,500' },
    { program: 'Bachelor of Science', duration: '3 Years', fee: '₹60,000', semester: '₹30,000' },
    { program: 'Bachelor of Commerce', duration: '3 Years', fee: '₹50,000', semester: '₹25,000' },
    { program: 'Master of Engineering', duration: '2 Years', fee: '₹1,20,000', semester: '₹60,000' },
    { program: 'Master of Business Administration', duration: '2 Years', fee: '₹1,50,000', semester: '₹75,000' },
    { program: 'Master of Science', duration: '2 Years', fee: '₹90,000', semester: '₹45,000' },
    { program: 'Doctor of Philosophy', duration: '3-5 Years', fee: '₹75,000', semester: '₹37,500' },
    { program: 'Integrated PhD', duration: '5 Years', fee: '₹1,00,000', semester: '₹50,000' }
  ];

  const deadlines = [
    { title: 'Application Opens', date: 'January 15, 2025', status: 'completed', description: 'Online application portal opens' },
    { title: 'Last Date to Apply', date: 'March 15, 2025', status: 'upcoming', description: 'Final deadline for application submission' },
    { title: 'Entrance Examination', date: 'April 10, 2025', status: 'upcoming', description: 'Written test and interview rounds' },
    { title: 'Result Declaration', date: 'May 5, 2025', status: 'upcoming', description: 'Final admission results announced' }
  ];

  const scholarships = [
    {
      title: 'Merit-Based Scholarship',
      description: 'Up to 100% tuition fee waiver for top academic performers. Renewable annually based on performance.',
      eligibility: 'Minimum 90% in qualifying examination',
      amount: 'Up to ₹1,50,000 per year',
      file: 'merit_scholarship_2025.pdf'
    },
    {
      title: 'Need-Based Financial Aid',
      description: 'Financial assistance for economically disadvantaged students from all backgrounds.',
      eligibility: 'Family income below ₹3,00,000 per annum',
      amount: 'Up to ₹75,000 per year',
      file: 'need_based_aid_2025.pdf'
    },
    {
      title: 'Research Excellence Grant',
      description: 'Special funding for PhD and research-oriented programs with monthly stipend.',
      eligibility: 'PhD students with research publications',
      amount: '₹25,000 per month + tuition waiver',
      file: 'research_grant_2025.pdf'
    },
    {
      title: 'Sports & Cultural Scholarship',
      description: 'Recognition and support for students with exceptional talents in sports and arts.',
      eligibility: 'State/National level achievements',
      amount: 'Up to ₹50,000 per year',
      file: 'sports_cultural_scholarship_2025.pdf'
    }
  ];

  return (
    <div>
      {/* Hero Section */}
      <section>
        <div>
          <div>
            <GraduationCap />
            <span>Academic Year 2025-26</span>
          </div>
          <h1>
            Admissions <span>2025</span>
          </h1>
          <p>Your journey to excellence begins here. Join India's premier institution and shape your future.</p>
          <div>
            <button>Apply Now</button>
            <button>Download Brochure</button>
          </div>
        </div>
      </section>

      {/* Fee Structure */}
      <section>
        <h2>Fee Structure</h2>
        <p>Transparent and competitive fee structure across all programs</p>
        <div>
          {/* UG Programs */}
          <div>
            <h3>UG Programs</h3>
            {feeStructure.slice(0, 3).map((program, index) => (
              <div key={index}>
                <h4>{program.program}</h4>
                <p>{program.duration}</p>
                <p>{program.fee}/year</p>
                <p>{program.semester}/sem</p>
              </div>
            ))}
          </div>

          {/* PG Programs */}
          <div>
            <h3>PG Programs</h3>
            {feeStructure.slice(3, 6).map((program, index) => (
              <div key={index}>
                <h4>{program.program}</h4>
                <p>{program.duration}</p>
                <p>{program.fee}/year</p>
                <p>{program.semester}/sem</p>
              </div>
            ))}
          </div>

          {/* PhD Programs */}
          <div>
            <h3>PhD Programs</h3>
            {feeStructure.slice(6, 8).map((program, index) => (
              <div key={index}>
                <h4>{program.program}</h4>
                <p>{program.duration}</p>
                <p>{program.fee}/year</p>
                <p>{program.semester}/sem</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Deadlines */}
      <section>
        <h2>Important Deadlines</h2>
        {deadlines.map((deadline, index) => (
          <div key={index}>
            <Calendar />
            <span>{deadline.status}</span>
            <h3>{deadline.title}</h3>
            <p>{deadline.date}</p>
            <p>{deadline.description}</p>
          </div>
        ))}
      </section>

      {/* Scholarships */}
      <section>
        <h2>Scholarships & Financial Aid</h2>
        {scholarships.map((scholarship, index) => (
          <div key={index}>
            <h3>{scholarship.title}</h3>
            <p>{scholarship.description}</p>
            <p><strong>Eligibility:</strong> {scholarship.eligibility}</p>
            <p>{scholarship.amount}</p>
            <button>
              <Download /> Download {scholarship.file}
            </button>
          </div>
        ))}
      </section>

      {/* Contact */}
      <section>
        <h2>Need Help?</h2>
        <div>
          <div>
            <Mail />
            <h3>Email Support</h3>
            <p>admissions@university.edu.in</p>
          </div>
          <div>
            <Phone />
            <h3>Phone Support</h3>
            <p>+91 1800-123-456</p>
          </div>
          <div>
            <Clock />
            <h3>Office Hours</h3>
            <p>9:00 AM - 6:00 PM IST</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Admissions;
