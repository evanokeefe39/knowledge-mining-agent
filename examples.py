import langextract as lx
example_sm_1 = lx.data.ExampleData(
    text="I think a lot of people are wishing for a business that has no difficulty. And if you find it, let me know. I've yet to see it. And I've looked at a lot of businesses. Many of you probably one don't need to change your business. Probably need to keep doing the business you're on. Number two, the business you're on is probably scalable. All businesses are scalable. It's just how hard is it to scale? And when we translate hard into what problems must I solve in order to scale it? And what are the alternative problems to this path that I would have to encounter if I didn't follow this path, which you'll find are often also equally difficult. And probably you're less equipped to solve them because you've never solved them before.",
    extractions=[
        lx.data.Extraction(
            extraction_class="Business Processes",
            extraction_text="scale it",
            attributes={"type": "main process", "description": "business scaling"}
        ),
        lx.data.Extraction(
            extraction_class="Business Processes",
            extraction_text="translate hard into what problems must I solve",
            attributes={"type": "sub-process", "description": "problem identification for scaling"}
        ),
        lx.data.Extraction(
            extraction_class="Strategies and Tactics",
            extraction_text="don't need to change your business",
            attributes={"type": "strategy", "goal": "maintain current operations"}
        ),
        lx.data.Extraction(
            extraction_class="Strategies and Tactics",
            extraction_text="keep doing the business you're on",
            attributes={"type": "tactic", "purpose": "consistency in operations"}
        ),
        lx.data.Extraction(
            extraction_class="Strategies and Tactics",
            extraction_text="translate hard into what problems must I solve in order to scale it",
            attributes={"type": "tactic", "purpose": "problem-solving approach to scaling"}
        ),
        lx.data.Extraction(
            extraction_class="Roles and Actors",
            extraction_text="you",
            attributes={"role": "business owner", "context": "decision-maker on scaling"}
        ),
        lx.data.Extraction(
            extraction_class="Roles and Actors",
            extraction_text="I",
            attributes={"role": "entrepreneur", "context": "speaker assessing businesses"}
        ),
        lx.data.Extraction(
            extraction_class="Outcomes and Results",
            extraction_text="business that has no difficulty",
            attributes={"outcome": "ideal but unrealized goal", "feasibility": "none observed"}
        ),
        lx.data.Extraction(
            extraction_class="Outcomes and Results",
            extraction_text="probably you're less equipped to solve them",
            attributes = {"outcome": "reduced capability", "condition": "new problems"}
        ),
        lx.data.Extraction(
            extraction_class="Relationships",
            extraction_text="translate hard into what problems must I solve in order to scale it",
            attributes={"type": "prerequisite", "description": "problem-solving required for scaling"}
        ),
        lx.data.Extraction(
            extraction_class="Relationships",
            extraction_text="alternative problems to this path that I would have to encounter if I didn't follow this path, which you'll find are often also equally difficult",
            attributes={"type": "part-whole", "description": "alternative paths have similar difficulties"}
        ),
        lx.data.Extraction(
            extraction_class="Relationships",
            extraction_text="you're less equipped to solve them because you've never solved them before",
            attributes={"type": "cause-effect", "description": "lack of experience reduces problem-solving ability"}
        ),
    ]
)
example_sm_2 = lx.data.ExampleData(
        text="A huge leg up that you can have is working one to three years in the industry that you want to get into. There's huge upside there because you don't even know what you don't know and you learn so many like default ways of operating. Kind of like if you're building an IKEA desk, right? If you don't have the directions and you have the pieces, you might eventually figure it out. But it's so much it takes so much more time than having a model to look at because you automatically know. You're like, 'Okay, well, first thing I'm going to do is I'm going to separate my tools over here. I'm put my screws over here and then I'm going to put my my blocks over here.' Great. So, it's the first thing that's what you do. But if you have no idea and you've never built a table before, you never built anything before, then it's way harder to",
        extractions=[
            lx.data.Extraction(
                extraction_class="Business Processes",
                extraction_text="working one to three years in the industry",
                attributes={"type": "main process", "description": "gaining industry experience"}
            ),
            lx.data.Extraction(
                extraction_class="Business Processes",
                extraction_text="learning default ways of operating",
                attributes={"type": "sub-process", "description": "acquiring operational knowledge"}
            ),
            lx.data.Extraction(
                extraction_class="Strategies and Tactics",
                extraction_text="working one to three years in the industry",
                attributes={"type": "strategy", "goal": "prepare for business entry"}
            ),
            lx.data.Extraction(
                extraction_class="Roles and Actors",
                extraction_text="you",
                attributes={"role": "aspiring entrepreneur", "context": "industry newcomer"}
            ),
            lx.data.Extraction(
                extraction_class="Tools and Systems",
                extraction_text="IKEA desk directions",
                attributes={"type": "model/framework", "purpose": "guidance for operations"}
            ),
            lx.data.Extraction(
                extraction_class="Tools and Systems",
                extraction_text="tools, screws, blocks",
                attributes={"type": "components", "purpose": "structured assembly"}
            ),
            lx.data.Extraction(
                extraction_class="Outcomes and Results",
                extraction_text="huge upside",
                attributes={"benefit": "knowledge acquisition", "impact": "reduced difficulty"}
            ),
            lx.data.Extraction(
                extraction_class="Outcomes and Results",
                extraction_text="takes so much more time",
                attributes={"outcome": "increased effort", "condition": "without model"}
            ),
            lx.data.Extraction(
                extraction_class="Relationships",
                extraction_text="working one to three years in the industry because you learn so many like default ways of operating",
                attributes={"type": "cause-effect", "description": "experience leads to operational knowledge"}
            ),
            lx.data.Extraction(
                extraction_class="Relationships",
                extraction_text="having a model to look at because you automatically know",
                attributes={"type": "prerequisite", "description": "model enables efficient execution"}
            ),
        ]
    )

example_sm_3 = lx.data.ExampleData(
    text="If you're getting started, for you to get 10 customers who pay you with it never giving anything away for free is going to take a long time. You getting 10 people to start working with you for free and then using the 10 testimonials you get there to then get your 11th, 12th, 13, 14th, 15, 16, 17, 18, 19, 20th customer is going to take you less time to get that 10 paying customers if you do 10 for free first of whatever it is that you Oh.",
    extractions=[
        lx.data.Extraction(
            extraction_class="Business Processes",
            extraction_text="get 10 customers who pay you",
            attributes={"type": "main process", "description": "customer acquisition for paid services"}
        ),
        lx.data.Extraction(
            extraction_class="Business Processes",
            extraction_text="getting 10 people to start working with you for free",
            attributes={"type": "sub-process", "description": "initial free engagement"}
        ),
        lx.data.Extraction(
            extraction_class="Business Processes",
            extraction_text="using the 10 testimonials you get there to then get your 11th, 12th, 13, 14th, 15, 16, 17, 18, 19, 20th customer",
            attributes={"type": "sub-process", "description": "conversion using testimonials"}
        ),
        lx.data.Extraction(
            extraction_class="Metrics",
            extraction_text="10 customers",
            attributes={"type": "quantity", "context": "initial paid customer target"}
        ),
        lx.data.Extraction(
            extraction_class="Metrics",
            extraction_text="10 people",
            attributes={"type": "quantity", "context": "free engagement target"}
        ),
        lx.data.Extraction(
            extraction_class="Metrics",
            extraction_text="11th, 12th, 13, 14th, 15, 16, 17, 18, 19, 20th customer",
            attributes={"type": "quantity", "context": "subsequent paid customers"}
        ),
        lx.data.Extraction(
            extraction_class="Metrics",
            extraction_text="take a long time",
            attributes={"type": "time metric", "condition": "without free offer"}
        ),
        lx.data.Extraction(
            extraction_class="Metrics",
            extraction_text="less time",
            attributes={"type": "time metric", "condition": "with free offer and testimonials"}
        ),
        lx.data.Extraction(
            extraction_class="Strategies and Tactics",
            extraction_text="getting 10 people to start working with you for free and then using the 10 testimonials",
            attributes={"type": "strategy", "goal": "accelerate paid customer acquisition"}
        ),
        lx.data.Extraction(
            extraction_class="Strategies and Tactics",
            extraction_text="do 10 for free first",
            attributes={"type": "tactic", "purpose": "build credibility"}
        ),
        lx.data.Extraction(
            extraction_class="Roles and Actors",
            extraction_text="you",
            attributes={"role": "new business starter", "context": "entrepreneur getting started"}
        ),
        lx.data.Extraction(
            extraction_class="Roles and Actors",
            extraction_text="10 customers",
            attributes = {"role": "paying customers", "context": "target audience"}
        ),
        lx.data.Extraction(
            extraction_class="Roles and Actors",
            extraction_text="10 people",
            attributes={"role": "initial free users", "context": "early adopters"}
        ),
        lx.data.Extraction(
            extraction_class="Tools and Systems",
            extraction_text="testimonials",
            attributes={"type": "method", "purpose": "marketing leverage"}
        ),
        lx.data.Extraction(
            extraction_class="Outcomes and Results",
            extraction_text="take a long time",
            attributes={"outcome": "slow growth", "condition": "no free offer"}
        ),
        lx.data.Extraction(
            extraction_class="Outcomes and Results",
            extraction_text="take you less time",
            attributes={"outcome": "faster growth", "condition": "using free offer and testimonials"}
        ),
        lx.data.Extraction(
            extraction_class="Relationships",
            extraction_text="getting 10 people to start working with you for free and then using the 10 testimonials you get there to then get your 11th, 12th, 13, 14th, 15, 16, 17, 18, 19, 20th customer",
            attributes={"type": "sequential", "description": "free engagement → testimonials → paid customers"}
        ),
        lx.data.Extraction(
            extraction_class="Relationships",
            extraction_text="do 10 for free first is going to take you less time to get that 10 paying customers",
            attributes={"type": "cause-effect", "description": "free offer reduces time to paid customers"}
        ),
    ]
)

examples = [example_sm_1, example_sm_2, example_sm_3]