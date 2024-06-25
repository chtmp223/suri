You will be given a text and its corresponding instruction, which contains the text's main goal and a constraint. Determine whether the text satisfies the constraint (not the main goal). You should return your answer (Yes/No/Partially) along with your reasoning and a quote in the text that supports your reasoning (the quote should not contain any double quotation marks). Your answer should contain 3 fields: "answer", "reasoning", and "quote". DO NOT output anything else other than the response, which starts with "<<" and ending with ">>".


# Example 1: The text satisfies the constraint. 
- Main goal: Write a first-person narrative describing a serene morning in a remote village
- Constraint: You must not use the letter 'e'. 
- Text: Dawn cracks with a yawn. On a hill, a hut sits, tranquil. Bright light climbs, casting gold on grass. In this calm morning, air is cool, birds sing softly. I stroll down paths, sipping hot cocoa, watching day start. Such is this dawn's charm, lifting spirits, as world awakens.
- Your response: <<"answer": "Yes", "reasoning": "The text does not contain any 'e', which satisfies the constraint.", "quote": "Dawn cracks with a yawn...">>


# Example 2: The text does not satisfy the constraint. 
- Main goal: Compose a narrative that takes place entirely within the confines of a single, small room. 
- Constraint: The story must not include any direct interaction or communication with other characters, whether through dialogue, notes, or any form of digital communication.
- Text: Sarah sat quietly in the corner of the small, dimly lit library room, surrounded by towering bookshelves filled with dusty volumes. Her focus was broken by a soft knock on the door. "Sarah, are you there?" her friend Emily's voice called out gently from the other side. Sarah, startled yet relieved to hear a familiar voice, responded, "Yes, I'm here, Emily. Just give me a moment, I'll open the door." They spent the next hour talking about the books Sarah had been reading and their plans for the weekend, making the small room feel a lot less lonely.
- Your response: <<"answer": "No", "reasoning": "The text includes a dialogue between Sarah and Emily, while the constraint specifies that the story must not include any direct interaction.", "quote": "'Sarah, are you there?' her friend Emily's voice called out gently from the other side. Sarah, startled yet relieved to hear a familiar voice, responded, 'Yes, I'm here, Emily. Just give me a moment, I'll open the door.'">>

# Example 3: The text only satisfies part of the constraint. 
- Main goal: Write a short story in which the protagonist meets an animal. 
- Constraint: The walk should take place in a public space in a summer day. 
- Text: As John strolled through the park one crisp autumn morning, he noticed the usual red and gold leaves blanketing the path. Today, however, a stray dog, thin and shivering, approached him. He hesitated, then offered his hand for the dog to sniff. It flinched at first, but soon warmed up to him. As they walked together, John wondered if he should take it home or find its owner. 
- Your response: <<"answer": "Partially", "reasoning": "The text mentions that the character walks in a park, which satisifies the constraint that the setting is a public place. However, the walk takes place in an autumn morning, which violates the constraint that the walk takes place in a summer day", "quote": "As John strolled through the park one crisp autumn morning, he noticed the usual red and gold leaves blanketing the path...">>


# Instruction 
## Main Goal
{goal}

## Constraint
{constraint}

# Text
{text}

DO NOT output anything else other than the response, which starts with "<<" and ending with ">>".
# Your response