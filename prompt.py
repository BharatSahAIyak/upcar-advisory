prompt="""
You are an agent tasked with analyzing agro-advisory data from a txt file text. Your objective is to extract specific information and ensure the JSON structure matches the provided format. The Pydantic code provided defines the structure of the JSON response to be generated. Your task is to ensure that the JSON output adheres to this structure and includes appropriate descriptions for each field.
References:
Definition of crops:
- Crops will include crops like: wheat, maize, zaid, sugarcane, oilseeds, and other crops, etc.
Definition of subgroups:
- Subgroups are: pulses, vegetables, horticulture, animal husbandry, poultry, fisheries, sericulture, forestry, etc.

Details:

1. Names of Crops:
Extract the names crops and subgroups whose advisory is mentioned in the PDF. Provide them in lowercase. Important: Exclude any names_of_crops items for which there is no corresponding advisory.

2. General advisory
Extract the general advisory which is in the beginning of the text generally. General advisory lines are followed by crop based advisories. Y
ou can find general advisory as:
> Heading: In the current scenario of weather in the state, farmers have to manage their agriculture for the next two weeks.The following recommendations are made: -
> Content of general advisory: n lines of general advisory.
You have to include all theese n lines of content in general advisory string by identifying the heading of heneral advisory. Keep n lines in list.

3. Crops Data:
Extract details of crops and subgroups.
These details are given in this format in the text:
> Wheat cultivation
> <line 1>
> <line 2>
> ...
> <line n>
> Vegetable cultivation
> <line 1>
> <line 2>
> ...
> <line n>
> fisheries
> <line 1>
> <line 2>
> ...
> <line n>
> zaid crops
> <line 1>
> <line 2>
> ...
> <line n>
... and so on for other crops and subgroups.

For above example, key will be name of crops or subgroup (wheat and vegetable cultivation in above example) and advisory will be the n lines there. Do this for all the crops and subgroups and all the lines of it.


Note: There are multiple lines for advisories. Limit to 200 words without leaving any noun and its reference behind.
Also, do not leave subgroups if there in text: pulses, vegetables, horticulture, animal husbandry, poultry, fisheries, sericulture, forestry, etc.

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

