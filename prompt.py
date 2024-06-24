prompt="""
You are an agent tasked with analyzing agro-advisory data from a txt file text. Your objective is to extract specific information and ensure the JSON structure matches the provided format. The Pydantic code provided defines the structure of the JSON response to be generated. Your task is to ensure that the JSON output adheres to this structure and includes appropriate descriptions for each field.
References:
Definition of crops:
- Crops will include crops like: wheat, paddy, maize, shri anna, pigeon pea, soybean, sesame, zaid, sugarcane, oilseeds, and other crops, etc.
Definition of subgroups:
- Subgroups are: pulses, vegetables, horticulture, animal husbandry, poultry, fisheries, sericulture, forestry, etc.

Details:

1. Names of Crops:
Extract the names crops and subgroups whose advisory is mentioned in the txt. Provide them in lowercase. Important: Exclude any names_of_crops items for which there is no corresponding advisory.

2. General advisory
Extract the general advisory which is in the beginning of the text generally. General advisory lines are followed by crop based advisories. You can find general advisory as:
> Heading: In the current scenario of weather in the state, farmers have to manage their agriculture for the next two weeks.The following recommendations are made: -
> Content of general advisory: n lines of general advisory.
You have to include all these n lines of content in general advisory string by identifying the heading of general advisory.

3. Crops Data:
Extract details of BOTH CROPS and SUBGROUPS.

Example of how you will find the details:

'''
<name of any crops or subgroups>
<line 1>
<line 2>
...
<line n>

<name of any crops or subgroups>
<line 1>
<line 2>
...
<line n>

<name of any crops or subgroups>
<line 1>
<line 2>
> ...
<line n>

<name of any crops or subgroups>
<line 1>
<line 2>
...
<line n>

... and so on for other crops and subgroups.
where:
crops you might find = wheat, paddy, maize, shri anna, pigeon pea, soybean, sesame, zaid, sugarcane, oilseeds, and other crops which you think are crops, etc.
subgroups you might find = pulses, vegetables, horticulture, animal husbandry, poultry, fisheries, sericulture, forestry, etc.
'''

For above example, only 4 are shown but there can be many crops and subgroups in the text. Key will be name of crops or subgroup and advisory will be the n lines there. Do this for all the crops and subgroups and all the lines of it. 
Don't create headings by yourself, only those headings which have dedicated data in points below the headings are to be taken as keys. 


Note:  
1. Do not leave subgroups if there in text: pulses, vegetables, horticulture, animal husbandry, poultry, fisheries, sericulture, forestry, etc.
2. Strictly follow the schema according to pydanctic class given below.

Pydantic classes for json structure:

from pydantic import BaseModel, Field
from typing import Dict, List, Tuple

class CropsData(BaseModel):
    advisory: List[str] = Field(..., description="Advisory information for the crop")

class AgroAdvisory(BaseModel):
    names_of_crops: List[str] = Field(..., description="Names of all crops/animal husbandry/poultry/fishing")
    general_advisory: str = Field(..., description="General advisory about weather and cropping")
    crops_data: Dict[str, CropsData] = Field(..., description="Details of each crops/animal husbandry/poultry/fishing")
"""

summary_prompt='''
You are provided with a json having agro advisory data. 
You have to do the task of trimming WHENEVER word_count > 250 for specific keys.

Keys to look for:
1. general_advisory
2. advisory (there will be multiple advisory keys i.e 1 for each crop)

How to count word_count:
1. general_advisory: value if a string, just count len(str)
2. advisory: value is a list of strings. for line in list: count+=len(line)

Trimming task:
1. We don't exactly want summarization. Check if limit is exceeding 250 at each advisory level then do the trimming.
2. Remove the extra words to keep the limit to 250 words at advisory level. Don't shorten it too much. We just want to stay within 250 words limit, else we're good with details.
3. Each advisory should be trimmed to keep the most important points, retain key nouns, and ensure that crucial information is not omitted.

Note: 
1. Schema of the json not to be hindered.
3. Strictly follow the pydantic class below for retaining schema.

Pydantic classes for json structure:

from pydantic import BaseModel, Field
from typing import Dict, List, Tuple

class CropsData(BaseModel):
    advisory: List[str] = Field(..., description="Advisory information for the crop")

class AgroAdvisory(BaseModel):
    names_of_crops: List[str] = Field(..., description="Names of all crops/animal husbandry/poultry/fishing")
    general_advisory: str = Field(..., description="General advisory about weather and cropping")
    crops_data: Dict[str, CropsData] = Field(..., description="Details of each crops/animal husbandry/poultry/fishing")

Here is the input:
'''

schema=schema = {
    "type": "object",
    "properties": {        
        "names_of_crops": {"type": "array", "items": {"type": "string"}},
        "general_advisory": {"type": "string"},
        "crops_data": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "advisory": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["advisory"]
            }
        }
    },
    "required": ["names_of_crops", "general_advisory", "crops_data"]
}

