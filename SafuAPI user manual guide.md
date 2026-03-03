SafuAPI user manual guide
Created by william.ww@binance.com, last modified on Feb 23, 2026
Support: @SAFUAPISupport Bot on Wea
OpenAI GPT-4.1 model - Chat Completion with Image recognition

OpenAI GPT-4.1 model - Streaming response

OpenAI o1 model

OpenAI o3-mini model

OpenAI gpt-4.1, gpt-5.1 models

OpenAI gpt-5models

DeekSeek R1 Chat Completion

Claude-models (e.g., Claude3.5 Sonnet)

Gemini models (supports reading video, audio, image)

Other models (e.g., Llama, Mistral, Amazon Titan, AI21 labs, stable diffusion, etc.)

Structured Output (GPT-4.1 model)

Translate Texts (Traditional Translator)

Translate Texts (Google Translate)

Translate Texts (AI, GPT-4.1)

Translate PDF

Translate Images Files

OCR (Extract texts in the images and PDFs)

Language support for translation

Detect Languages in Texts, Image, PDF

Content Moderation

Embedding

Supported Models

API Endpoints

OpenAI SDK (Python and Java)

Anthropic SDK (For Claude models)

API Key Application

Pricing charges

Context window

Flow Architecture

Known Issues

API endpoint
Dev

https://safuapi.dev.secfdg.net

Prod

https://safuapi.prod.secfdg.net

Usage:
Chat Completion with Vision Image recognition (OpenAI GPT4o model)
## Request
 
curl -XPOST "https://safuapi.dev.secfdg.net/openai/deployments/gpt-4.1/chat/completions?api-version=2024-10-21" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw '{
    "max_tokens": 4096,
    "temperature": 0.7,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": null,
    "response_format": {
        "type": "text"
    },
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What is in the image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "AWS_S3_PRESIGNED_URL"
                    }
                }
            ]
        }
    ]
}'
 
# The above messages.content[1].image_url.url can also be base64 encoding of the image. For example as follows.
# "messages": [{"role": "user","content": [{"type": "text","text": "What is in the image?"},{"type": "image_url","image_url": {"url": "data:image/png;base64,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"}}]}]
 
# For the `response_format` param above, use {"type": "json_object"} if you want to guarantee response is a valid json object. When using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request.
# Setting 'type' to 'text' will make the AI return choices.message.content in non-json, see the example Response below.
 
## Response
 
{
    "id": "chatcmpl-AICQPrBlOj7Z6CCNY3WiwmQzIS0ne",
    "object": "chat.completion",
    "created": 1728901029,
    "model": "gpt-2024-05-13",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "The image shows a black silhouette of a person inside a black circle. This symbol is often used to represent a person or an individual and is commonly seen in various contexts, such as public signage and iconography."
            },
            "logprobs": null,
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 1002,
        "completion_tokens": 10,
        "total_tokens": 1012
    },
    "system_fingerprint": "fp_67802d9a6d"
}
Chat Completion texts only (OpenAI models)
## Request
 
curl -XPOST "https://safuapi.dev.secfdg.net/openai/deployments/gpt-4.1/chat/completions?api-version=2024-10-21" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw '{
    "messages": [{"role":"user","content":"What is crypto curency?"}],
    "max_tokens": 4096,
    "temperature": 0.7,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": null
}'
 
## Response
 
{"id": "chatcmpl-8nItZY4I5SKpa3i0tsURCQ8g8omRd", "object": "chat.completion", "created": 1706761397, "model": "gpt-4", "prompt_filter_results": [{"prompt_index": 0, "content_filter_results": {"hate": {"filtered": false, "severity": "safe"}, "self_harm": {"filtered": false, "severity": "safe"}, "sexual": {"filtered": false, "severity": "safe"}, "violence": {"filtered": false, "severity": "safe"}}}], "choices": [{"finish_reason": "stop", "index": 0, "message": {"role": "assistant", "content": "Cryptocurrency is a type of digital or virtual currency that uses cryptography for security. It operates independently of a central bank and is based on blockchain technology, which acts as a distributed ledger enforced by a disparate network of computers. Bitcoin is the most popular cryptocurrency, but there are thousands of others including Ethereum, Ripple, and Litecoin."}, "content_filter_results": {"hate": {"filtered": false, "severity": "safe"}, "self_harm": {"filtered": false, "severity": "safe"}, "sexual": {"filtered": false, "severity": "safe"}, "violence": {"filtered": false, "severity": "safe"}}}], "usage": {"prompt_tokens": 12, "completion_tokens": 65, "total_tokens": 77}}
Chat completion curl response formatted JSON Expand source
Chat Completion with streaming response (OpenAI GPT4o model)
## Request
 
curl -XPOST "https://safuapi.dev.secfdg.net/openai/deployments/gpt-4.1/chat/completions?api-version=2024-10-21" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw '{
    "max_tokens": 4096,
    "temperature": 0,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": null,
    "response_format": {"type": "text"},
    "messages": [{"role": "user","content": [{"type": "text","text": "What is crypto currency?"}]}],
    "stream": true
}'
 
## Response
 
# Please read this document for how streaming response works: https://cookbook.openai.com/examples/how_to_stream_completions
 
{
    "id": "chatcmpl-AIsbrUxXcgT1xGYVMA0sSwKLmRQKm",
    "object": "chat.completion.chunk",
    "created": 1729063187,
    "model": "gpt-2024-05-13",
    "system_fingerprint": "fp_67802d9a6d",
    "choices": [
        {
            "index": 0,
            "delta": {
                "content": "Crypto currency "
            },
            "finish_reason": null
        }
    ]
}
....Response stream....
DeepSeek R1 Chat Completion
## Request
 
## Fully compatible with DeepSeek API format here: https://api-docs.deepseek.com/
 
curl --location 'https://safuapi.dev.secfdg.net/chat/completions' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \ # Also support bearer token authentication. Change this to: "Authorization: Bearer SAFUAPI_API_KEY"
--data '{
    "model": "DeepSeek-R1",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hey"
        }
    ],
    "stream": false # Change to true if you want streaming.
}'
 
## Response (Non-streaming)
 
{
    "id": "84ca357917a143c5a34963cf3d330c84",
    "object": "chat.completion",
    "created": 1740394606,
    "model": "deepseek-r1",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "<think>\nAlright, the user sent \"Hey\". That's pretty casual. Let me see... They probably want to start a conversation or ask for something.\n\nFirst, I should respond in a friendly and approachable way. Maybe say hello and ask how I can assist them today. Keeping it open-ended so they feel comfortable to ask anything.\n\nAlso, since it's just \"Hey\", maybe they're testing the waters or unsure how to proceed. I'll make sure my response encourages them to share what's on their mind without pressure.\n\nOkay, I'll go with something like, \"Hello! How can I assist you today?\" to keep it simple and helpful.\n</think>\n\nHello! How can I assist you today?",
                "tool_calls": null,
                "reasoning_content": null
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "total_tokens": 156,
        "completion_tokens": 146,
        "prompt_tokens_details": null
    }
}
 
## Response (Streaming)
## See full sample here: https://deepinfra.com/deepseek-ai/DeepSeek-V3/api
 
data: {"id": "Rc5hsIPHOSfMP3rNSFUw9tfR", "object": "chat.completion.chunk", "created": 1694623354, "model": "deepseek-ai/DeepSeek-R1", "choices": [{"index": 0, "delta": {"role": "assistant", "content": " "}, "finish_reason": null}]}
 
...
...
 
data: {"id": "Rc5hsIPHOSfMP3rNSFUw9tfR", "object": "chat.completion.chunk", "created": 1694623354, "model": "deepseek-ai/DeepSeek-R1", "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
 
data: [DONE]
Structured Output (JSON)
## Available in both Dev and Prod environment.
 
## Request 
## More info on the request body: https://openai.com/index/introducing-structured-outputs-in-the-api/
 
curl --location 'https://safuapi.dev.secfdg.net/openai/deployments/gpt-4.1/chat/completions?api-version=2024-10-21' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data '{
    "messages": [
        {
            "role": "system",
            "content": "Extract the event information."
        },
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday."
        }
    ],
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "CalendarEventResponse",
            "strict": true,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "date": {
                        "type": "string"
                    },
                    "participants": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "name",
                    "date",
                    "participants"
                ],
                "additionalProperties": false
            }
        }
    }
}'
 
## Response
### The choices.0.message.content will be a valid JSON format.
 
{
    "choices": [
        {
            "content_filter_results": {
                "hate": {
                    "filtered": false,
                    "severity": "safe"
                },
                "self_harm": {
                    "filtered": false,
                    "severity": "safe"
                },
                "sexual": {
                    "filtered": false,
                    "severity": "safe"
                },
                "violence": {
                    "filtered": false,
                    "severity": "safe"
                }
            },
            "finish_reason": "stop",
            "index": 0,
            "logprobs": null,
            "message": {
                "content": "{\"name\":\"Science Fair\",\"date\":\"Friday\",\"participants\":[\"Alice\",\"Bob\"]}",
                "role": "assistant"
            }
        }
    ],
    "created": 1726718494,
    "id": "chatcmpl-A92eE0AJ1gjdClkfxF0BHItnSJo2l",
    "model": "gpt-2024-08-06",
    "object": "chat.completion",
    "prompt_filter_results": [
        {
            "prompt_index": 0,
            "content_filter_results": {
                "hate": {
                    "filtered": false,
                    "severity": "safe"
                },
                "jailbreak": {
                    "filtered": false,
                    "detected": false
                },
                "self_harm": {
                    "filtered": false,
                    "severity": "safe"
                },
                "sexual": {
                    "filtered": false,
                    "severity": "safe"
                },
                "violence": {
                    "filtered": false,
                    "severity": "safe"
                }
            }
        }
    ],
    "system_fingerprint": "fp_b2ffeb16ee",
    "usage": {
        "completion_tokens": 17,
        "prompt_tokens": 33,
        "total_tokens": 50
    }
}
Chat Completion (gpt-o1)
## Request 
 
curl --location 'https://safuapi.dev.secfdg.net/openai/deployments/gpt-o1/chat/completions?api-version=2025-03-01-preview' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data '{
    "messages": [
        {
            "role": "user",
            "content": "A princess is as old as the prince will be when the princess is twice as old as the prince was when the princess'\''s age was half the sum of their present age. What is the age of prince and princess? Provide all solutions to this question."
        }
    ],
    "max_completion_tokens": 32768,
    "frequency_penalty": 0,
    "presence_penalty": 0
}'
 
## Response
 
## It takes 3 minutes to get the following response. o1 is slow but very smart.
 
{"choices": [{"content_filter_results": {"hate": {"filtered": false, "severity": "safe"}, "protected_material_code": {"filtered": false, "detected": false}, "protected_material_text": {"filtered": false, "detected": false}, "self_harm": {"filtered": false, "severity": "safe"}, "sexual": {"filtered": false, "severity": "safe"}, "violence": {"filtered": false, "severity": "safe"}}, "finish_reason": "stop", "index": 0, "message": {"content": "To solve this problem, let's break it down step by step and translate the words into mathematical equations.\n\nLet\u2019s denote:\n- \\( P \\) = current age of the prince\n- \\( S \\) = current age of the princess\n\n**1. The princess is as old as the prince will be when...**\n\nThis translates to:\n\\[ S = P + t \\]\nwhere \\( t \\) is the number of years from now when this condition is met.\n\n**2. ...the princess is twice as old as the prince was when the princess's age was half the sum of their present ages.**\n\nFirst, find when the princess's age was half the sum of their present ages.\n\nLet \\( x \\) be the number of years ago when this happened. Then:\n\\[ S - x = \\frac{1}{2}(S + P) \\]\n\nSimplify this equation:\n\\[ 2(S - x) = S + P \\]\n\\[ 2S - 2x = S + P \\]\n\\[ S - 2x = P \\]\n\\[ S - P = 2x \\]\n\\[ x = \\frac{S - P}{2} \\]\n\n**Now, at that time (x years ago), the prince's age was** \\( P - x \\).\n\nWe know from earlier:\n\\[ S = P + t \\]\nSo:\n\\[ t = S - P \\]\n\nSubstitute \\( t \\) into the expression for \\( x \\):\n\\[ x = \\frac{t}{2} \\]\n\\[ t = 2x \\]\n\n**Now, the princess will be twice as old as the prince was at that time:**\n\\[ S + y = 2(P - x) \\]\nBut from the first condition, the princess's current age equals the prince\u2019s age at that future time:\n\\[ S = P + y \\]\n\\[ y = S - P \\]\n\nSubstitute \\( y \\) back into the previous equation:\n\\[ S + (S - P) = 2(P - x) \\]\n\\[ 2S - P = 2P - 2x \\]\n\\[ 2S - P = 2P - 2\\left(\\frac{S - P}{2}\\right) \\]\n\\[ 2S - P = 2P - (S - P) \\]\n\\[ 2S - P = 2P - S + P \\]\n\\[ 2S - P = 2P + P - S \\]\n\\[ 2S - P = 3P - S \\]\n\\[ 2S + S = 3P + P \\]\n\\[ 3S = 4P \\]\n\\[ S = \\frac{4P}{3} \\]\n\n**Therefore, the princess\u2019s age is \\(\\frac{4}{3}\\) times the prince\u2019s age.**\n\nSince ages are whole numbers, let\u2019s let the prince's age be a multiple of 3:\n\\[ P = 3k \\]\nThen:\n\\[ S = \\frac{4 \\times 3k}{3} = 4k \\]\n\n**Thus, the ages are:**\n- Prince: \\( P = 3k \\)\n- Princess: \\( S = 4k \\)\n\nFor any positive integer \\( k \\).\n\n**All solutions are:**\n\n| \\( k \\) | Prince's Age (\\( P \\)) | Princess's Age (\\( S \\)) |\n|---------|----------------------|------------------------|\n| 1       | 3                    | 4                      |\n| 2       | 6                    | 8                      |\n| 3       | 9                    | 12                     |\n| 4       | 12                   | 16                     |\n| 5       | 15                   | 20                     |\n| 6       | 18                   | 24                     |\n| ...     | ...                  | ...                    |\n\n**Answer:**\n\nAn explicit answer:\u2003The prince is any multiple of 3 years, the princess is 4\u20443 times his age.\n\nThat is:\n- Prince\u2019s age = 3\u202f\u00d7\u202fany positive integer\n- Princess\u2019s age = 4\u202f\u00d7\u202fthat integer", "role": "assistant"}}], "created": 1729221047, "id": "chatcmpl-AJXfz3UgBcITMAm42sJP1mjYgbgYI", "model": "o1-preview-2024-09-12", "object": "chat.completion", "prompt_filter_results": [{"prompt_index": 0, "content_filter_results": {"custom_blocklists": {"filtered": false}, "hate": {"filtered": false, "severity": "safe"}, "jailbreak": {"filtered": false, "detected": false}, "self_harm": {"filtered": false, "severity": "safe"}, "sexual": {"filtered": false, "severity": "safe"}, "violence": {"filtered": false, "severity": "safe"}}}], "system_fingerprint": "fp_50cdd5dc04", "usage": {"completion_tokens": 5700, "completion_tokens_details": {"reasoning_tokens": 4800}, "prompt_tokens": 58, "prompt_tokens_details": {"cached_tokens": 0}, "total_tokens": 5758}}
Chat Completion (gpt-o3-mini)
## Request
 
### o3-mini model is the most cost-efficient model that support reasoning.
### It supports 3 reasoning_effort options: low, medium, and high. This flexibility allows o3‑mini to “think harder” when tackling complex challenges or prioritize speed when latency is a concern.
### o3‑mini does not support vision capabilities, so developers should continue using o1 model for visual reasoning tasks.
### For more request parameters, please consult: https://learn.microsoft.com/en-us/azure/ai-services/openai/reference-preview#request-body-2
 
 
curl --location 'https://safuapi.dev.secfdg.net/openai/deployments/gpt-o3-mini/chat/completions?api-version=2025-03-01-preview' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data '{
    "messages": [
        {
            "role": "user",
            "content": "How to calculate the speed of light?"
        }
    ],
    "max_completion_tokens": 100000,
    "reasoning_effort": "low",
    "model": "o3-mini"
}'
 
## Response
 
{
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "logprobs": null,
            "message": {
                "content": "There are several ways to “calculate” or determine the speed of light, both theoretically and experimentally. Here are a few key approaches:\n\n1. Theoretical Calculation using Fundamental Constants:\n • The speed of light (c) in a vacuum is related to the vacuum permeability (μ₀) and the vacuum permittivity (ε₀) by the equation:\n  c = 1/√(μ₀ × ε₀)\n • In the International System of Units (SI), μ₀ (the permeability of free space) is defined as exactly 4π × 10⁻⁷ N/A². The permittivity of free space, ε₀, can be defined in terms of the speed of light using the relation:\n  ε₀ = 1/(μ₀ × c²)\n • Historically, when ε₀ and μ₀ were measured independently, one could calculate c from these measurements. Today, however, the speed of light is defined as exactly 299,792,458 m/s, and ε₀ is determined based on this definition.\n\n2. Experimental Methods:\n a. Time-of-Flight Measurements:\n  • One can emit a pulse of light toward a mirror at a known distance and measure the time it takes for the light to travel to the mirror and back. The speed is then calculated as:\n   c = (2 × distance) / (time delay)\n  • This method requires very precise timing equipment since light travels extremely fast.\n\n b. Fizeau's Toothed Wheel Experiment:\n  • In 1849, Hippolyte Fizeau used a rapidly rotating toothed wheel to intermittently block and unblock the light beam. By adjusting the rotational speed so that the light passing through one gap was blocked on its return by the next tooth, he was able to calculate its speed using the known spacing on the wheel and distance to the reflector.\n\n c. Foucault’s Rotating Mirror Technique:\n  • Léon Foucault later improved on Fizeau’s experiment by using a rotating mirror instead of a toothed wheel. The change in the angle of the reflected beam, due to the mirror’s rotation during the light’s travel time, allowed a precise determination of the speed of light.\n\n3. Modern Techniques:\n • With the advent of lasers, interferometry, and atomic clocks, the speed of light can now be determined with extremely high accuracy using sophisticated equipment.\n • It’s important to note that since 1983, the meter has been defined in terms of the speed of light. In effect, the speed of light is no longer “measured” but fixed by definition at exactly 299,792,458 m/s. This means that other units (like the meter) are defined based on this constant.\n\nSummary:\n• The equation c = 1/√(μ₀ε₀) provides a theoretical calculation, and several ingenious experiments (time-of-flight, Fizeau’s and Foucault’s methods) provide experimental measurements.\n• Today, instead of “calculating” c from experimental data, we use its defined exact value as a fundamental constant in physics.\n\nThis should give you a comprehensive overview of how the speed of light is calculated and measured.",
                "refusal": null,
                "role": "assistant"
            }
        }
    ],
    "created": 1744020331,
    "id": "chatcmpl-BJde7j1zGVc532uCh3JJ6VX3QmJpd",
    "model": "o3-mini-2025-01-31",
    "object": "chat.completion",
    "system_fingerprint": "fp_ded0d14823",
    "usage": {
        "completion_tokens": 877,
        "completion_tokens_details": {
            "accepted_prediction_tokens": 0,
            "audio_tokens": 0,
            "reasoning_tokens": 192,
            "rejected_prediction_tokens": 0
        },
        "prompt_tokens": 14,
        "prompt_tokens_details": {
            "audio_tokens": 0,
            "cached_tokens": 0
        },
        "total_tokens": 891
    }
}
gpt-5.1, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano
## Request
 
### Increased context window limit up to 1M (1,047,576) input tokens!
### This models is specifically targeted for better coding and instruction following, making it better at handling complex technical and coding problems.
### Support Text, image processing; JSON Mode; parallel function calling; Enhanced accuracy and responsiveness; Parity with English text and coding tasks compared to GPT-4 Turbo with Vision; Support for enhancements; Support for complex structured outputs.
### Speed: gpt-4.1-nano > gpt-4.1-mini > gpt-4.1
### Can start with gpt-4.1-mini model as is balances speed and performance.
 
#curl --location 'https://safuapi.dev.secfdg.net/openai/deployments/gpt-5.1/chat/completions?api-version=2025-03-01-preview' \
#curl --location 'https://safuapi.dev.secfdg.net/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview' \
#curl --location 'https://safuapi.dev.secfdg.net/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2025-01-01-preview' \
curl --location 'https://safuapi.dev.secfdg.net/openai/deployments/gpt-4.1-mini/chat/completions?api-version=2025-01-01-preview' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data '{
    "messages": [
        {
            "role": "user",
            "content": "Please help me summarize the following super long texts: ..."
        }
    ],
    "max_completion_tokens": 32768,
    "temperature": 1,
    "stream": false
}'
 
## Response
 
{
    "choices": [
        {
            "content_filter_results": {},
            "finish_reason": "stop",
            "index": 0,
            "logprobs": null,
            "message": {
                "content": "Paris is an amazing city with a rich history, world-class art, and vibrant neighborhoods. Here’s a list of must-see attractions and a few suggestions for unique experiences:\n\n### **Iconic Landmarks**\n- **Eiffel Tower** – Go up for incredible views or enjoy a picnic on the Champ de Mars.\n- **Louvre Museum** – Home to the Mona Lisa and thousands of other masterpieces (consider booking tickets in advance).\n- **Notre-Dame Cathedral** – Still beautiful from the outside and the area around Île de la Cité is well worth exploring.\n- **Arc de Triomphe** – Climb to the top for a spectacular city panorama.\n- **Sainte-Chapelle** – Stunning stained glass windows, less crowded and truly breathtaking.\n\n### **Quintessential Paris**\n- **Montmartre & Sacré-Cœur** – Wander this bohemian neighborhood, see the artist square, and enjoy views from the basilica steps.\n- **Le Marais** – Trendy neighborhood with historic sites, boutiques, and fantastic cafés.\n- **Latin Quarter** – Full of bookshops (including Shakespeare & Company), old streets, and the Luxembourg Gardens.\n\n### **Art and Culture**\n- **Musée d'Orsay** – Impressionist and post-Impressionist art in a stunning former railway station.\n- **Centre Pompidou** – Modern art collection and great city views from the terrace.\n- **Rodin Museum** – Beautiful sculpture garden.\n  \n### **For Something Different**\n- **Père Lachaise Cemetery** – Resting place of Jim Morrison, Edith Piaf, and Oscar Wilde.\n- **Canal Saint-Martin** – Hip area, lovely for a stroll or a picnic.\n- **Covered Passages** – 19th-century shopping arcades like Galerie Vivienne.\n- **Palace of Versailles** – Short train ride from Paris; incredible gardens and history.\n\n### **Local Experiences**\n- **Café culture** – Sit at a terrace café for people-watching with coffee or wine.\n- **Boulangeries & Pâtisseries** – Try croissants, pain au chocolat, and a macaron or two.\n- **Seine River Cruise** – Especially magical at night.\n- **Picnic** in one of the many parks (Luxembourg Gardens, Tuileries).\n\n### **Seasonal/Events**\n- If you’re in Paris when museums are free (first Sunday of the month except summer), take advantage!\n- Check for temporary exhibits or concerts at major venues.\n\nLet me know your interests, if you have limited time, or if you want tips for a certain type of experience—food, fashion, hidden gems, etc.!",
                "refusal": null,
                "role": "assistant"
            }
        }
    ],
    "created": 1744800304,
    "id": "chatcmpl-BMuYKm9HXjXYeNOJQYkmNACZWVyaK",
    "model": "gpt-4.1-2025-04-14",
    "object": "chat.completion",
    "prompt_filter_results": [
        {
            "prompt_index": 0,
            "content_filter_results": {
                "hate": {
                    "filtered": false,
                    "severity": "safe"
                },
                "jailbreak": {
                    "filtered": false,
                    "detected": false
                },
                "self_harm": {
                    "filtered": false,
                    "severity": "safe"
                },
                "sexual": {
                    "filtered": false,
                    "severity": "safe"
                },
                "violence": {
                    "filtered": false,
                    "severity": "safe"
                }
            }
        }
    ],
    "system_fingerprint": "fp_4bdf61b929",
    "usage": {
        "completion_tokens": 549,
        "completion_tokens_details": {
            "accepted_prediction_tokens": 0,
            "audio_tokens": 0,
            "reasoning_tokens": 0,
            "rejected_prediction_tokens": 0
        },
        "prompt_tokens": 18,
        "prompt_tokens_details": {
            "audio_tokens": 0,
            "cached_tokens": 0
        },
        "total_tokens": 567
    }
}


gpt-5
## Request
 
curl --location 'https://safuapi.dev.secfdg.net/openai/responses?api-version=2025-04-01-preview' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer API_KEY_HERE' \
--data '{
    "model": "gpt-5",
    "input": "How much gold would it take to coat the Statue of Liberty in a 1mm layer?",
    "reasoning": {
        "effort": "minimal"
    }
}'
 
## Request with input_image.
 
curl --location 'https://safuapi.dev.secfdg.net/openai/responses?api-version=2025-04-01-preview' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer API_KEY_HERE' \
--data '{
    "model": "gpt-5",
    "input": [
      {
        "role": "user",
        "content": [
          { "type": "input_image", "image_url": "https://example.com/slide.jpg" },
          { "type": "input_text",  "text": "Describe this slide in 5 bullets." }
        ]
      }
    ],
    "reasoning": {
        "effort": "minimal"
    }
}'
 
## Response
 
{
    "id": "resp_6895730088848190bcff083fcb505b12020724ae7c1c68cd",
    "object": "response",
    "created_at": 1754624768,
    "status": "completed",
    "background": false,
    "content_filters": null,
    "error": null,
    "incomplete_details": null,
    "instructions": null,
    "max_output_tokens": null,
    "max_tool_calls": null,
    "model": "gpt-5",
    "output": [
        {
            "id": "rs_6895730147c88190927b1970755a90ca020724ae7c1c68cd",
            "type": "reasoning",
            "summary": []
        },
        {
            "id": "msg_689573018f2881909b8c89df17594091020724ae7c1c68cd",
            "type": "message",
            "status": "completed",
            "content": [
                {
                    "type": "output_text",
                    "annotations": [],
                    "text": "Short answer: about 14 metric tons of gold.\n\nHow it’s estimated:\n- The Statue of Liberty’s exterior copper skin area is roughly 2,100–2,350 m² (estimates vary; 2,250 m² is a reasonable midpoint).\n- A 1 mm coating is 0.001 m thick.\n- Gold volume needed ≈ area × thickness ≈ 2,250 m² × 0.001 m = 2.25 m³.\n- Gold density ≈ 19,320 kg/m³.\n- Mass ≈ 2.25 m³ × 19,320 kg/m³ ≈ 43,500 kg ≈ 43.5 metric tons.\n\nHowever, that assumes coating every bit of the skin. If you only coat the copper-clad exterior (excluding interior structure and base) and use a lower area estimate (~700–750 m² sometimes quoted just for the robe/visible front), you’d get much less. A commonly cited “effective” exterior area for coating computations lands closer to ~730 m²:\n- Volume ≈ 0.73 m³\n- Mass ≈ 0.73 × 19,320 ≈ 14,100 kg ≈ 14 metric tons.\n\nWhich number to use depends on the surface area definition:\n- Full copper skin (all around): roughly 40–45 tons.\n- More conservative “exposed frontal area” type estimate: roughly 14 tons.\n\nIf you want a single figure for the entire exterior skin all around, use about 44 metric tons. If you intended just the commonly visible exterior estimate, use about 14 metric tons."
                }
            ],
            "role": "assistant"
        }
    ],
    "parallel_tool_calls": true,
    "previous_response_id": null,
    "prompt_cache_key": null,
    "reasoning": {
        "effort": "minimal",
        "summary": null
    },
    "safety_identifier": null,
    "service_tier": "default",
    "store": true,
    "temperature": 1.0,
    "text": {
        "format": {
            "type": "text"
        }
    },
    "tool_choice": "auto",
    "tools": [],
    "top_p": 1.0,
    "truncation": "disabled",
    "usage": {
        "input_tokens": 25,
        "input_tokens_details": {
            "cached_tokens": 0
        },
        "output_tokens": 345,
        "output_tokens_details": {
            "reasoning_tokens": 0
        },
        "total_tokens": 370
    },
    "user": null,
    "metadata": {}
}

Claude models:
Chat Completion with Vision Image Recognition (Anthropic models)
## Request
## The image data is the base64 encoding of the image file.
## SafuAPI Claude model follow the same Request body format as AWS Bedrock: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html
## Also supports other Claude models, just replace the model ID with models listed in the "Other models" section of this doc: https://confluence.toolsfdg.net/pages/viewpage.action?spaceKey=SP&title=SafuAPI+user+manual+guide#SafuAPIusermanualguide-supported-models
 
curl -XPOST "https://safuapi.dev.secfdg.net/anthropic/deployments/claude-3.5-sonnet/chat/completions" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw '{
    "max_tokens": 4096,
    "system": "You are a Chief Financial Officer at a big International Company. Write in a professional tone.",
    "messages": [{"role": "user", "content": [
      {
        "type": "image",
        "source": {
          "type": "base64",
          "media_type": "image/png",
          "data": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII="
        }
      },
      {"type": "text", "text": "What is in this image?"}
    ]}]
}'
 
## Response (JSON)
 
{"id": "msg_01RSFzPDFjYCZFBAp3yRU2av", "type": "message", "role": "assistant", "content": [{"type": "text", "text": "This image is an overview of the Azure Monitor, a comprehensive monitoring and observability platform provided by Microsoft Azure. The image outlines the key components and capabilities of Azure Monitor, including:\n\n1. Application, Operating System, Azure Resources, Azure Subscription, Azure Tenant, and Custom Sources - which represent the different elements that can be monitored by Azure Monitor.\n\n2. Metrics, Logs, Visualize (Dashboards, Views, Power BI, Workbooks), Analyze (Metrics Explorer, Log Analytics), Respond (Alerts, Autoscale), Integrate (Event Hubs, Logic Apps, Ingest & Export APIs) - which represent the various monitoring, analysis, and integration features available within Azure Monitor.\n\nThe image provides a high-level overview of the Azure Monitor solution and its key capabilities, designed to help users understand the breadth of monitoring and observability services offered by the platform."}], "model": "claude-3.5-sonnet-48k-20240307", "stop_reason": "end_turn", "stop_sequence": null, "usage": {"input_tokens": 1622, "output_tokens": 198}}

Gemini models:
Gemini models (supports reading video, audio, image)
## Request
## Support reading video, audio, PDFs files, and images.
## Longest context windows so far! 1M (1,000,000) tokens Input context window.
## Supported models: search for "gemini" in this section https://confluence.toolsfdg.net/display/SP/SafuAPI+user+manual+guide#SafuAPIusermanualguide-supported-models
 
curl --location 'https://safuapi.dev.secfdg.net/v1beta/models/gemini-2.0-flash-001:generateContent' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data '{
    "contents": [
        {
            "role": "user",
            "parts": [
                {
                    "text": "There are two attachments, one is a video, another is an image. Is the ID card in the video the same as the ID card in the attached image?"
                },
                {
                    "fileData": {
                        "mimeType": "video/mp4",
                        "fileUri": "https://AWS_S3_PRESIGNED_URL"
                    }
                },
                {
                    "fileData": {
                        "mimeType": "image/png",
                        "fileUri": "https://AWS_S3_PRESIGNED_URL"
                    }
                },
                {
                    "fileData": {
                        "mimeType": "image/png",
                        "fileUri": "data:image/png;base64,iVBO......"
                    }
                }
            ]
        }
    ]
}'
 
## Response (String)
 
"No, the ID card in the video is not the same as the ID card in the attached image. The ID card in the video appears to be from Uzbekistan, while the ID card in the attached image is from Morocco."

More:
Chat Completion (Meta Llama models, and all other models)
## Request
## For all other models, such as Mistral, Amazon Titan, AI21 labs, stable diffusion, use the same path pattern as below, just replace the `llama-3-70b-instruct` to the models in the `Other models` table in this doc.
 
curl -XPOST "https://safuapi.dev.secfdg.net/safu/deployments/llama-3-70b-instruct/chat/completions" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw '{
    "prompt": "write hello world program in Python."
}'
 
## Response (JSON)
 
{"generation": " Here is the Python code to print \"Hello, World!\" on the screen:\n```\nprint(\"Hello, World!\")\n```\nThis is a very simple Python program. You can save this code in a file with a `.py` extension, for example, `hello.py`, and then run it using Python.\n\nHere is how you can do it:\n\n1. Open a text editor, such as Notepad on Windows or TextEdit on Mac.\n2. Type the above code in the text editor.\n3. Save the file with a `.py` extension, for example, `hello.py`.\n4. Open a terminal or command prompt.\n5. Navigate to the directory where you saved the file using the `cd` command. For example, if you saved the file on the desktop, you can navigate to the desktop using `cd Desktop`.\n6. Type `python hello.py` to run the program.\n7. Press Enter to execute the program.\n\nWhen you run the program, you should see \"Hello, World!\" printed on the screen.\n\nHere is the output:\n```\nHello, World!\n```\nCongratulations, you have just written and run your first Python program!\n\nNote: If you are using Python 2.x, you can use `print \"Hello, World!\"` instead of `print(\"Hello, World!\")`. However, in Python 3.x, `print` is a function, so you need to use parentheses.", "prompt_token_count": 7, "generation_token_count": 292, "stop_reason": "stop"}

Embedding
# Embeddings
 
## Request
 
curl -XPOST "https://safuapi.dev.secfdg.net/openai/deployments/text-embedding-ada-002/embeddings?api-version=2024-02-15-preview" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw "{\"input\": \"The food was delicious and the waiter...\"}"
 
## Response
 
{"object": "list", "data": [ { "object": "embedding", "index": 0, "embedding": [ 0.0023064255, -0.009327292, ... -0.0028842222 ] } ], "model": "ada", "usage": { "prompt_tokens": 8, "total_tokens": 8 } }
Dalle 3 Image Generation
# Dalle3 Image generation. For more info on parameters, read this doc https://learn.microsoft.com/en-us/azure/ai-services/openai/dall-e-quickstart?tabs=dalle3%2Ccommand-line&pivots=rest-api
 
## Request
 
curl -XPOST "https://safuapi.prod.secfdg.net/openai/deployments/dalle3/images/generations?api-version=2024-02-15-preview" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw "{
    \"prompt\": \"A multi-colored umbrella on the beach, disposable camera\",
    \"size\": \"1024x1024\",
    \"n\": 1,
    \"quality\": \"hd\",
    \"style\": \"vivid\"
    }"
 
## Response
 
{"created":1701791957,"data":[{"revised_prompt":"A photo depicting a bright multi-colored umbrella planted on a sandy beach. The brilliant hues of the umbrella stand in stark contrast to the beige sand and clear blue sky. On the tranquil and warm beach, a disposable camera lies in close proximity to the umbrella. This snapshot moment captures the essence of a sunny day by the sea.","url":"https://dalleprodsec.blob.core.windows.net/private/images/7764bd86-e555-4e05-a79c-f45fa85c4e06/generated_00.png?se=2023-12-06T15%3A59%3A34Z&sig=2WEi6XL%2Fk8UlZV%2BcZFOynwb1aaSnOa90XMX%2FNHl8YNw%3D&ske=2023-12-06T23%3A34%3A57Z&skoid=e52d5ed7-0657-4f62-bc12-7e5dbb260a96&sks=b&skt=2023-11-29T23%3A34%3A57Z&sktid=33e01921-4d64-4f8c-a055-5bdaffd5e33d&skv=2020-10-02&sp=r&spr=https&sr=b&sv=2020-10-02"}]}

Text Translation (Traditional Translator)
# Text Translation by Traditional Translator.
# This translator has average latency of 400ms, and is generally faster than the /ai-text-translate below.
 
# Sample Request:
 
curl -XPOST "https://safuapi.dev.secfdg.net/translate" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw '{
    "html_mode": false,
    "target_language": "english",
    "contents": ["Hola", "listo muchas gracias"]
    "source_language": "spanish" # Optional. If the source_language is not given, then SafuAPI will auto detect the source language. It's recommended to add source_language because it increases the translation accuracy.
}'
 
# If the "html_mode" parameter is set to true, then the translation engine will not translate HTML tags such as <p color='yellow'>, </i>, etc.
 
# Sample Response
 
["Hello", "Ready, thank you very much"]

Google Translate
# Google Translate.
# This translator has average latency of 400ms, and is generally faster than the /ai-text-translate below.
 
# Sample Request:
 
curl -XPOST "https://safuapi.dev.secfdg.net/google-translate" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw '{
    "target_language": "english",
    "contents": ["Hola", "listo muchas gracias"]
}'
 
# Sample Response
 
["Hello", "Okay, thank you very much."]

Text Translation (AI, GPT-4o Large Language Model)
# Text Translation by AI. GPT-4o large language model. It has enhanced accuracy for people names, home addresses, and with given background contexts.
# For input less than 100 characters, the average latency is 1 second. Longer input texts will incur longer latency.
 
# Sample Request:
 
curl -XPOST "https://safuapi.dev.secfdg.net/ai-text-translate" \
--header "Content-Type: application/json" \
--header "api-key: 1234abcd-3030-2020-aidk-examplekey" \
--data-raw '{
    "model": "gpt-4.1-mini", # Default model is gpt-4.1-mini because the quality is acceptable and cost effective.
    "target_language": "english",
    "contents": ["雷","云龙","上海","淮海路9999号"]
}'
 
# Sample Response
[
    "Lei",
    "Yunlong",
    "Shanghai",
    "9999 Huaihai Road"
]

PDF Translation
# PDF Translation. Input a PDF, return a PDF in which the texts are translated into a target_language.
 
# Sample Request:
 
curl --location 'https://safuapi.dev.secfdg.net/translate-pdf' \
--remote-name \
--remote-header-name \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data-raw '{
  "user_email": "user@binance.com",
  "url": "https://hutchesonlab.fiu.edu/wp-content/uploads/sample-pdf.pdf",
  "target_language": "chinese"
}'
 
# If you use S3 bucket to store file, you can create a Presigned URL for the S3 file, and set the url as the presigned url.
# For `user_email`, if multiple users will have access to the file, you can put a generic value such as "kyc@binance.com". This email will be printed on every page of the PDF file. This is meant to trace who leaked the PDF file to external world.
# The --remote-name & --remote-header-name above will save the returned PDF file to local directory and set the PDF file name as in the response header.
 
# Sample Response
 
The HTTP response body will be the bytes stream of the translated PDF file. If you use CURL command like above, it will save the returned PDF file to local directory.

Image Translation
# Image Translation. Input a image file, return a image in which the texts are translated into a target_language. Image file such as .png, .jpg, etc.
 
# Sample Request:
 
curl --location 'https://safuapi.dev.secfdg.net/translate-image' \
--remote-name \
--remote-header-name \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data-raw '{
  "user_email": "user@binance.com",
  "url": "https://upload.wikimedia.org/wikipedia/commons/6/60/Screenshot_of_Wikipedia%27s_Screenshot_page_Jan_2019.png",
  "target_language": "chinese"
}'
 
# If you use S3 bucket to store file, you can create a Presigned URL for the S3 file, and set the url as the presigned url.
# For `user_email`, if multiple users will have access to the file, you can put a generic value such as "kyc@binance.com". This email will be printed on the image file. This is meant to trace who leaked the file to external world.
# The --remote-name & --remote-header-name above will save the returned file to local directory and set the file name as in the response header.
 
# Sample Response
 
The HTTP response body will be the bytes stream of the translated Image file. If you use CURL command like above, it will save the returned file to local directory.

Get languages supported by translation
# Return a list of languages supported by /translate.
 
curl -XGET --location 'https://safuapi.dev.secfdg.net/translate/languages' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey'
 
# Return a list of languages supported by /translate-image.
 
curl -XGET --location 'https://safuapi.dev.secfdg.net/translate-image/languages' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey'
 
## For languages supported by /translate-pdf, if the PDF content is text, then it uses the same languages list as above /translate/languages.
## If the PDF content is image, then it uses the same language list as above /translate-image/languages.
 
## The source language of /translate-image/languages is a subset of /translate/languages. Specifically, text languages supported ~22 more source languages than image translation.
 
# Sample Response
{
  "source_languages": ["chinese", "english", ...],
  "target_languages": ["chinese", "english", ...]
}

OCR (Extract texts in the images and PDFs)
# Extract texts in the images and PDFs.
# Input the URL of image/PDF file, return the texts in the file.
 
# Sample Request:
 
curl --location 'https://safuapi.dev.secfdg.net/ocr' \
--remote-name \
--remote-header-name \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data '{
    "url": "https://hutchesonlab.fiu.edu/wp-content/uploads/sample-pdf.pdf"  # If you use S3 bucket to store file, you can create a Presigned URL for the S3 file, and set the url as the presigned url.
}'
 
# Sample Response. "raw_paragraphs" is a list of all paragraphs in the image or PDF.
 
{
    "raw_paragraphs": [
        "This is a Sample PDF file"
    ]
}

Detect languages in Text, Image, PDF
# Return a list of languages existing in Text, Image, PDF.
 
## Either a `url` or `text` should be given in a request, but not both.
## If debug is true, languages_to_texts will be returned.
 
# Sample Request:
 
curl --location 'https://safuapi.dev.secfdg.net/detect-language' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data-raw '{
  "url": "https://hutchesonlab.fiu.edu/wp-content/uploads/sample-pdf.pdf",
  "text": "Danke, BINANCE!",
  "debug": true
}'
 
# Sample Response
# object key is language name, value is its frequency. The frequency is calculated by the number of characters of each language.
 
{
    "languages_to_frequency": {
        "english": 0.5,
        "german": 0.5
    },
    "languages_to_texts": {
        "english": [
            "BINANCE",
            ...
        ],
        "german": [
            "Danke"
        ]
    }
}

Content Moderation
# Detect inappropriate contents such as related to sex, violence, LLM Jailbreak.
# Average latency is 300ms.
# Input text size limit is 10,000 characters. Please contact SafuAPISupport Bot to increase this limit for you.
 
# Sample Request:
 
curl --location 'https://safuapi.dev.secfdg.net/content-moderation' \
--header 'Content-Type: application/json' \
--header 'api-key: 1234abcd-3030-2020-aidk-examplekey' \
--data '{
    "text": "How to be a porn star?"
}'
 
 
# Sample Response (JSON list)
# The severity could be 0,2,4,6 (The higher value indicate it's more severe)
 
[
    {
        "category": "Hate",
        "severity": 0
    },
    {
        "category": "SelfHarm",
        "severity": 0
    },
    {
        "category": "Sexual",
        "severity": 4
    },
    {
        "category": "Violence",
        "severity": 0
    },
    {
        "category": "Jailbreak-attacks",
        "severity": 0
    }
]
OpenAI Python SDK
pip install openai


Note: Please remove slash "/" at the end of api endpoint. 

Example:

https://safuapi.prod.secfdg.net/ → Incorrect

https://safuapi.prod.secfdg.net → Correct


Links to Official Code Examples below were used with latest versions: openai==1.59.7 and pydantic==2.10.5

Chat Completion Example:

https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?tabs=command-line%2Cjavascript-keyless%2Ctypescript-keyless%2Cpython-new&pivots=programming-language-python

Structured Output Example:

https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/structured-outputs?tabs=python

Python SDK
# Python3
  
from openai import AzureOpenAI
 
# Azure OpenAI client initialization
client = AzureOpenAI(
    api_key=os.getenv("AZ_OPENAPI_KEY"),
    api_version="2024-08-01-preview",  # Update to your API version
    azure_endpoint='https://safuapi.dev.secfdg.net'
)
 
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
    {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
    {"role": "user", "content": "Do other Azure Cognitive Services support this too?"}
]
 
model_name = "gpt-4.1" # See all the supported model: https://confluence.toolsfdg.net/display/SP/SafuAPI+user+manual+guide#SafuAPIusermanualguide-supported-models
 
response = client.chat.completions.create(
    model=model_name,
    messages=messages,
    # tools=tools,
)
  
print(response.choices[0].message.content)
# Can also try response.model_dump_json() to retrieve the full response body.
  
# Python for Dalle3 Image generation. For more info on parameters, read this doc https://learn.microsoft.com/en-us/azure/ai-services/openai/dall-e-quickstart?tabs=dalle3%2Ccommand-line&pivots=rest-api
  
import requests
import time
import os
api_base = 'https://safuapi.prod.secfdg.net' # Enter your endpoint here
api_key = 'Your-API-key' # Enter your API key here
  
  
api_version = '2023-12-01-preview'
url = f"{api_base}/openai/deployments/dalle3/images/generations?api-version={api_version}"
headers= { "api-key": api_key, "Content-Type": "application/json" }
 
# Enter your prompt text here
body = {
    "prompt": "A multi-colored umbrella on the beach, disposable camera",
    "size": "1024x1024", # supported values are “1792x1024”, “1024x1024” and “1024x1792”
    "n": 1,
    "quality": "hd", # Options are “hd” and “standard”; defaults to standard
    "style": "vivid" # Options are “natural” and “vivid”; defaults to “vivid”
}
 
submission = requests.post(url, headers=headers, json=body)
  
image_url = submission.json()['data'][0]['url']
  
print(image_url)

https://github.com/anthropics/anthropic-sdk-python?tab=readme-ov-file#configuring-the-http-client

Anthropic SDK
import anthropic
client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=safukey,
    base_url='https://safuapi.dev.secfdg.net/anthropic/deployments/claude-3.5-sonnet'
)
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
print(message.content)
https://python.langchain.com/docs/tutorials/llm_chain/#using-language-models

Langchain Azure OpenAI
!pip install -qU langchain-core langgraph>0.2.27 langchain-openai
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
 
os.environ["AZURE_OPENAI_API_KEY"] = safukey
# Azure OpenAI client initialization using LangChain
model = AzureChatOpenAI(
    azure_endpoint='https://safuapi.dev.secfdg.net',  # Your Azure OpenAI endpoint
    openai_api_version='2024-10-21',  # Your API version
    azure_deployment='gpt-o1-mini',  # Replace with your model deployment name,
    temperature=1
)
print(model.invoke([HumanMessage(content="Hi! I'm Bob")]))
 
model = AzureChatOpenAI(
    azure_endpoint='https://safuapi.dev.secfdg.net',  # Your Azure OpenAI endpoint
    openai_api_version='2024-10-21',  # Your API version
    azure_deployment='gpt-4.1',  # Replace with your model deployment name
)
model.invoke([HumanMessage(content="Hi! I'm Bob")])
https://python.langchain.com/api_reference/anthropic/chat_models/langchain_anthropic.chat_models.ChatAnthropic.html#chatanthropic

Langchain Claude
!pip install -U langchain-anthropic
from langchain_anthropic import ChatAnthropic
import os
 
os.environ["ANTHROPIC_API_KEY"] = safukey
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    # api_key="...",
    base_url="https://safuapi.dev.secfdg.net/anthropic/deployments/claude-3.5-sonnet",
    # other params...
)
messages = [
    ("system", "You are a helpful translator. Translate the user sentence to French."),
    ("human", "I love programming."),
]
print(llm.invoke(messages))
OpenAI Java SDK
You can use Azure's OpenAI SDK , and input our API endpoint and API key in the following code.

OpenAI Java SDK
1
2
3
4
OpenAIClient client = new OpenAIClientBuilder()
    .credential(new AzureKeyCredential("{key}"))
    .endpoint("{endpoint}")
    .buildClient();
or

OpenAI Java SDK
1
2
3
4
OpenAIAsyncClient client = new OpenAIClientBuilder()
    .credential(new AzureKeyCredential("{key}"))
    .endpoint("{endpoint}")
    .buildAsyncClient();
Flow


API methods, and parameters
At the moment, we support OpenAI's Chats Completion method. We use the same API interface with Azure's OpenAI API, please consult Azure doc for the parameters for the method: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#chat-completions

Supported Model
OpenAI models: consult this doc for the details information of each models.
Dev

gpt35, → Deprecated on Nov.25.2024

gp40614, (GPT4 v0613) → Deprecated on Nov.25.2024

gpt4-32k-0614 (GPT4 32K v0613) → Deprecated on Nov.25.2024

gpt4-1106 (GPT4 Turbo v1106) → Deprecated on Nov.25.2024

dalle3 (Image generation)

text-embedding-ada-002 (Embeddings)

text-embedding-3-small 

gpt4o-latest

gpt-4o-2024-05-13 → Supports reading ID cards. Please see the known issues.

gpt-4o-mini → Fast, cheap model with fewer parameters.

gpt-o1 (The most sophisticated model as 2024.Oct. It's the smartest model but have long latency.)

gpt-o1-mini

gpt-4o-realtime (speech in, speech out conversational interactions)

gpt-o3-mini (fast, smart, cost effective model that supports reasoning)

gpt-4.1 (support 1M input tokens, better coding and instruction following) (supports Structured Outputs) 👍👍 Recommended!

gpt-4.1-mini (support 1M input tokens, balanced speed and response quality.) 👍👍 Recommended!

gpt-4.1-nano (support 1M input tokens, fastest in 4.1 series.)

gpt-o3 (Support reasoning)

gpt-o4-mini (Support reasoning)

gpt-5

gpt-5.1

gpt-5.1-chat

gpt-5.2

Prod

gpt35, → Deprecated on Nov.25.2024

gp40614, (GPT4 v0613) → Deprecated on Nov.25.2024

gpt4-32k-0614 (GPT4 32K v0613) → Deprecated on Nov.25.2024

gpt4-1106 (GPT4 Turbo v1106) → Deprecated on Nov.25.2024

dalle3 (Image generation)

text-embedding-ada-002 (Embeddings)

text-embedding-3-small

gpt4o-latest

gpt-4o-2024-05-13 → Supports reading ID cards. Please see the known issues.

gpt-4o-mini → Fast, cheap model with fewer parameters.

gpt-o1 (The most sophisticated model as 2024.Oct. It's the smartest model but have long latency.)

gpt-o1-mini

gpt-4o-realtime (speech in, speech out conversational interactions)

gpt-o3-mini (fast, smart, cost effective model that supports reasoning)

gpt-4.1 (support 1M input tokens, better coding and instruction following) (supports Structured Outputs) 👍👍 Recommended!

gpt-4.1-mini (support 1M input tokens, balanced speed and response quality.) 👍👍 Recommended!

gpt-4.1-nano (support 1M input tokens, fastest in 4.1 series.)

gpt-o3 (Support reasoning)

gpt-o4-mini (Support reasoning)

gpt-5

gpt-5.1

gpt-5.1-chat

gpt-5.2

     2. Other models: consult this doc for the detailed information of each models.

Dev and Prod

claude-sonnet-4-5-20250929-v1

claude-opus-4-20250514-v1 → Good at coding!

claude-sonnet-4-20250514-v1 → Good at coding!

claude-3-7-sonnet-20250219-v1 (Support Image Vision, and Text input) → 👍👍 Recommended!
claude-3.5-sonnet (Support Image Vision, and Text input)

claude-3.5-sonnet-v2-20241022 → Supported Computer Use. Learn how to use it. 

claude-3-sonnet (Support Image Vision, and Text input)

claude-3-haiku (Support Image Vision, and Text input)
claude-3-opus (Support Image Vision, and Text input)

jamba-instruct
titan-text-g1---express
titan-text-g1---lite
titan-text-premier
titan-embeddings-g1---text
titan-embedding-text-v2
titan-multimodal-embeddings-g1
titan-image-generator-g1claude-instant
jurassic-2-mid
jurassic-2-ultra
command
command-light
command-r
command-r+
embed-english
embed-multilingual
llama-3-8b-instruct
llama-3-70b-instruct
mistral-7b-instruct
mixtral-8x7b-instruct
mistral-large
mistral-small
stable-diffusion-xl

DeepSeek-R1 → AI models that supports thinking process.

gemini-3-pro-preview

gemini-3-flash-preview

gemini-2.5-pro

gemini-2.5-flash

gemini-2.5-flash-lite

gemini-2.0-flash-001

gemini-2.0-flash-lite 

gemini-3.1-pro-preview

-> Gemini models are able to read Videos, Audios, and PDFs. Also support the longest context length of 1M tokens. Also supports more gemini models-version here: https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-pro

Context windows limitations per request
Model

Maximum token window limit (1 token ~= 4 characters)

gpt35

4,096 tokens (~5 pages of document)

gpt4	
8,192 tokens (~10 pages of document)

gpt4 (32k)	
32,768 tokens (~40 pages of document)

gpt4-1106	
128,000 tokens (~160 pages of document)

gpt4o-latest (version 2024-08-06)	
Input: 128,000 tokens (~160 pages of document)

Output: 16,384 tokens

text-embedding-ada-002	
Input: 8191 tokens.

Output dimension fixed at 1536.

text-embedding-3-small	
Input: 8191 tokens.

Output dimension fixed at 1536.

gpt-4o-mini	
Input: 128,000 tokens (~160 pages of document)

Output: 16,384 tokens

gpt-o1	
Input: 128,000 tokens (~160 pages of document)

Output: 32,768 tokens

gpt-o1-mini	
Input: 128,000 tokens (~160 pages of document)

Output: 65,536 tokens

gpt-o3-mini	
Input: 200,000 tokens

Output: 100,000 tokens

gpt-4.1

gpt-4.1-mini

gpt-4.1-nano

Input: 1,047,576 tokens

Output: 32.768 tokens

gemini-2.5-pro
gemini-2.5-flash
gemini-2.5-flash-lite-preview-06-17
gemini-2.0-flash-001
gemini-2.0-flash-lite

Input: 1,000,000 tokens.

Model

Maximum token window limit(1 token ~= 4 characters)

Claude3-*

200,000 tokens (~250 pages of document)

Pricing charges
Model

Price

gpt35

Input (User Prompt): 1.5 USD per 1M (1,000,000) tokens.

Output (AI response): 2 USD per 1M (1,000,000) tokens.

gp40614

Input (User Prompt): 30 USD per 1M (1,000,000) tokens.

Output (AI response): 60 USD per 1M (1,000,000) tokens.

gpt4-32k-0614

Input (User Prompt): 60 USD per 1M (1,000,000) tokens.

Output (AI response): 120 USD per 1M (1,000,000) tokens.

gpt4-1106	
Input (User Prompt): 10 USD per 1M (1,000,000) tokens.

Output (AI response): 30 USD per 1M (1,000,000) tokens.

gpt4o-latest
(version 2024-08-06)	
Input (User Prompt): 2.5 USD per 1M (1,000,000) tokens.

Output (AI response): 10 USD per 1M (1,000,000) tokens.

text-embedding-ada-002	
Input (User Prompt): 0.1 USD per 1M (1,000,000) tokens.

text-embedding-3-small	
Input (User Prompt): 0.02 USD per 1M (1,000,000) tokens.

gpt-4o-mini	
Input (User Prompt): 0.15 USD per 1M (1,000,000) tokens.

Output (AI response): 0.6 USD per 1M (1,000,000) tokens.

gpt-o1	
Input (User Prompt): 15 USD per 1M (1,000,000) tokens.

Output (AI response): 60 USD per 1M (1,000,000) tokens.

gpt-o1-mini	
Input (User Prompt): 3 USD per 1M (1,000,000) tokens.

Output (AI response): 12 USD per 1M (1,000,000) tokens.

dalle3	
[For HD quality]

Resolution: 1024 * 1024 → 8 USD per 100 images.

Resolution: 1024 * 1792 → 12 USD per 100 images.

claude-3-haiku	
Input (User Prompt): 0.25 USD per 1M (1,000,000) tokens.

Output (AI response): 1.25 USD per 1M (1,000,000) tokens.

claude-3.5-sonnet	
Input (User Prompt): 3 USD per 1M (1,000,000) tokens.

Output (AI response): 15 USD per 1M (1,000,000) tokens.

command-r+	
Input (User Prompt): 3 USD per 1M (1,000,000) tokens.

Output (AI response): 15 USD per 1M (1,000,000) tokens.

/translate (Text)	
$10 per million characters

gpt-o3-mini	
Input: $1.10 USD per 1M (1,000,000) tokens.

Output: $4.40 USD per 1M (1,000,000) tokens.

gpt-4.1	
Input: $2.0 USD per 1M (1,000,000) tokens.

Output: $8 USD per 1M (1,000,000) tokens.

gpt-4.1-mini	
Input: $0.4 USD per 1M (1,000,000) tokens.

Output: $1.6 USD per 1M (1,000,000) tokens.

gpt-4.1-nano	
Input: $0.15 USD per 1M (1,000,000) tokens.

Output: $0.6 USD per 1M (1,000,000) tokens.

API-Version
For the query string parameter `api-version`, please consult this doc. The api-version varies for different methods.

WAF IP whitelist
If you request to the API endpoint directly, it might return HTTP 403 error because your client IP was blocked by WAF. To add your Client IP to IP whitelist, please create a JIRA ticket in this group: https://jira.toolsfdg.net/projects/SECURITY/issues/

and provide below info in the ticket:

Your team's name
The contact email for the API users. We will contact this email if we found abnormal behavior from the API users.
The IPs that will be visiting the SafuAPI. If it visit through Internet, please provide client's public IPs. If it visit through private network such as VPC peering or VPC endpoint, please provide client's private IP.
Background of usage cases. What will your team use the SafuAPI for?

Request internal access
If you want to request to the API within AWS VPC network or your service does not have a internet-public interface, You might create a PrivateLink with SAFAPI endpoint. Please follow the steps below:

Create a connection request to service name com.amazonaws.vpce.ap-northeast-1.vpce-svc-06c43092ccecd9161.
Contact @SAFUAPISupport Bot on Wea to approve the connection request.
Ensure your security groups of the VPC Endpoint are configured to allow access to TCP port 443.
Add a private DNS Record safuapi.prod.secfdg.net pointing to your VPC Endpoint.
API key application
Please go to this doc.

Rate Limits
To ensure the API works normally, by default, we applied the following limits for each API Key.

request_per_minute_limit

7000
The example scenario for the first limit request_per_minute_limit.

API key1 sent 5 requests at 00:00:01, 00:00:02, 00:00:03, 00:00:04, 00:00:05, respectively. When the API key1 sends a new request at 00:00:06, it will receive an HTTP error message "request throttled. request_per_minute_limit exceeded." When it sends a new request at 00:01:01, that new request will not be throttled.

The example scenario for the second limit token_per_minute_limit.

API key1 sent 2 requests at 00:00:01, 00:00:02, and consuming 4000 and 4000 computation token respectively. When the API key1 sends a new request at 00:00:03, it will receive an HTTP error message "request throttled. token_per_minute_limit exceeded."

Tokens in OpenAI: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/overview

Azure OpenAI processes text by breaking it down into tokens. Tokens can be words or just chunks of characters. For example, the word “hamburger” gets broken up into the tokens “ham”, “bur” and “ger”, while a short and common word like “pear” is a single token. Many tokens start with a whitespace, for example “ hello” and “ bye”.

The total number of tokens processed in a given request depends on the length of your input, output and request parameters. The quantity of tokens being processed will also affect your response latency and throughput for the models.

Token calculator by OpenAI: https://platform.openai.com/tokenizer

SafuAPI API key application
Created by william.ww@binance.com, last modified on Jan 08, 2026
Please click here and create a Jira ticket. The ticket needs to be in the "SECURITY" project folder, if you did not see the security folder, then choose the "TECH" project folder. And then send the ticket URL to SAFUAPISupport Bot on Wea. Someone will generate an API Key for you. Please provide information listed below.

User's Binance.com email address.
Business Use Case description.
What models would you use? such as gpt4o-latest, etc
Do you have a strong requirement for request rates? such as 100 requests per minute.
What is the expected number of input characters in a request? For example, 1000 characters per request? If you don't specify, we estimate by 4000 characters per request. (1 token ~= 4 characters.)
What is the client side network environment? please provide below info of the client side. We need these info to whitelist your server IP to access safuapi. (If you only need to request from your local Macbook, then you can skip this question.)

[Required] Public Outbound IPs that your resources use to connect to the Internet. Such as 52.2.2.1.
[Required] AWS account ID
[Optional] VPC ID
[Optional] Subnet IDs
[Optional] Resource ID such as EC2, EKS, ECS, etc ID?


Created by dennis.n@binance.com, last modified by ky.o@binance.com on Jan 12, 2026
SAFUGPT Plus API is compatible with openai format. You can refer to their official document. https://platform.openai.com/docs/api-reference/chat/create

Just replace the base url with https://safuapi.prod.secfdg.net/safugpt/api and use the SafuAPI token created at SafuAPI API key application

Base url
https://safuapi.prod.secfdg.net/safugpt/api



List Models (deprecated)
curl --location 'https://safuapi.prod.secfdg.net/safugpt/api/models' \
  --header 'Authorization: Bearer <safuapi_token>'
List Models
curl --location 'https://safuapi.prod.secfdg.net/safugpt/api/v1/models/list' \
  --header 'Authorization: Bearer <safuapi_token>'
Chat Completion 
curl --location 'https://safuapi.prod.secfdg.net/safugpt/api/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <safuapi_token>' \
--data '{
    "model": "gpt-4.1-mini",
    "messages": [
        {
            "role": "user",
            "content": "hi"
        }
    ]
}'
Chat Completion with Knowledge Bases
curl --location 'https://safuapi.prod.secfdg.net/safugpt/api/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <safuapi_token>' \
--data '{
    "model": "gpt-4.1-mini",
    "messages": [
        {
            "role": "user",
            "content": "hi"
        }
    ],
    "files": [
        {
            # full context search
            "id": "your_knowledge_base_id", # min required permission: read
            "type": "collection", # required
            "context": "full" # optional, include to enable full context search
        },
        {
            # without context: turn on semantic search
            "id": "your_knowledge_base_id",
            "type": "collection"
        }
    ]
}'


Created by ky.o@binance.com, last modified on Dec 17, 2025
List knowledge base

Endpoint: {{GET /knowledge/}}

curl 'https://safuapi.prod.secfdg.net/safugpt/api/v1/knowledge/' \
 
  -H 'authorization: Bearer <safuapi_token>' \
 
  -H 'content-type: application/json'
Get specific knowledge base
Endpoint: {{GET /knowledge/1234}}

curl 'https://safuapi.prod.secfdg.net/safugpt/api/v1/knowledge/{kb_id}' \
 
  -H 'authorization: Bearer <safuapi_token>' \
 
  -H 'content-type: application/json'

Upload File
Upload a file to the SAFU API system.

Endpoint: {{POST /files/}}

Content-Type: {{multipart/form-data}}

Example Request
curl --location 'https://safuapi.prod.secfdg.net/safugpt/api/v1/files/' \
  --header 'Content-Type: multipart/form-data' \
  --header 'Authorization: Bearer <safuapi_token>' \
  -F 'name=file' \
  -F 'filename=test.txt' \
  -F 'Content-Type=text/plain'
Success Response
Status Code: {{200 OK}}

Response Body:

{
  "id": "string",
  "user_id": "string", 
  "hash": "string",
  "filename": "string"
}

Add File to Knowledge Base
Associate an uploaded file with a specific knowledge base using the file ID from the upload response.

Endpoint: {{POST /knowledge/{knowledge_base_id}/file/add}}

Content-Type: {{application/json}}

Path Parameters
knowledge_base_id	string	✓	Unique identifier of the target knowledge base
Request Body

{
  "file_id": "{uploaded_file_id}"
}


Request Body Parameters
file_id	string	✓	The ID of the previously uploaded file
Example Request

curl 'https://safuapi.prod.secfdg.net/safugpt/api/v1/knowledge/{knowledge_base_id}/file/add' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <safuapi_token>' \
  --data '{"file_id":"{uploaded_file_id}"}'

Success Response
Status Code: {{200 OK}}

Response Body:

{
  "id": "string",
  "user_id": "string",
  "name": "string", 
  "description": "string"
}

Complete Workflow Example
Here's a complete example of uploading a file and adding it to a knowledge base:

Step 1: Upload the file

# Upload file and capture the response

curl --location 'https://safuapi.prod.secfdg.net/safugpt/api/v1/files/' \
  --header 'Content-Type: multipart/form-data' \
  --header 'Authorization: Bearer your_token_here' \
  -F 'name=file' \
  -F 'filename=document.pdf' \
  -F 'Content-Type=application/pdf'


Response:

{
  "id": "file_12345",
  "user_id": "user_67890",
  "hash": "abc123def456",
  "filename": "document.pdf"
}

Step 2: Add file to knowledge base

# Use the file ID from step 1

curl 'https://safuapi.prod.secfdg.net/safugpt/api/v1/knowledge/kb_98765/file/add' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer your_token_here' \
  --data '{"file_id":"file_12345"}'


Response:

{
  "id": "kb_98765",
  "user_id": "user_67890", 
  "name": "My Knowledge Base",
  "description": "A collection of important documents"
}

Update file content of Knowledge Base (v2)
Request Body Parameters
file_id	string	✓	The ID of the uploaded file
content	string	✓	The file content to be updated


curl 'https://safuapi.prod.secfdg.net/safugpt/api/v2/knowledge/{kb_id}/file/update' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer your_token_here' \
  --data '{"file_id":"file_12345", "content": "content_to_be_replace_or_update"}'

Delete file from Knowledge Base
Request Body Parameters
file_id	string	✓	The ID of the uploaded file


curl 'https://safuapi.prod.secfdg.net/safugpt/api/v1/knowledge/{kb_id}/file/remove' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer your_token_here' \
  --data '{"file_id":"file_12345"}'


  Created by ky.o@binance.com, last modified on Nov 06, 2025
Request Body Sample

{
  "id": "custom-gpt-4",
  "base_model_id": "openai/gpt-4.1",
  "name": "Custom GPT-4 Model",
  "meta": {
    "profile_image_url": "/static/favicon.png",
    ...
  },
  "params": {
    "system":"custom prompt",
    "temperature":0.1
    ...
  },
  "is_active": true
}


Create Custom Model

curl 'https://safuapi.prod.secfdg.net/safugpt/api/v1/models/create' \
 
  -H 'authorization: Bearer <safuapi_token>' \
 
  -H 'content-type: application/json' \
 
  --data-raw '{"id":"custom-model","base_model_id":"openai/gpt-4.1-mini","name":"Custom Model","meta":{"profile_image_url":"/static/favicon.png","description":"custom model","suggestion_prompts":null,"tags":[],"capabilities":{"vision":true,"file_upload":true,"web_search":true,"image_generation":true,"video_generation":true,"code_interpreter":false,"citations":false,"status_updates":false,"usage":false},"knowledge":[]},"params":{"system":"custom prompt","temperature":0.1},"access_control":{"read":{"group_ids":[],"user_ids":[]},"write":{"group_ids":[],"user_ids":[]}}}'


Create Custom Model V2

Use the knowledge base ID instead of the full object, unlike in v1.

Note: v2 support full object and id as input in the array.

meta.knowledge (array of ids) = ["6dfc33ed-e63f-42a7-9a65-d76f73711102", "kb_id_2", {"id": "6dfc33ed-e63f-42a7-9a65-d76f73711102", ...}]

curl 'https://safuapi.prod.secfdg.net/safugpt/api/v2/models/create' \
 
  -H 'authorization: Bearer <safuapi_token>' \
 
  -H 'content-type: application/json' \
 
  --data-raw '{"id":"custom-model","base_model_id":"openai/gpt-4.1-mini","name":"Custom Model","meta":{"profile_image_url":"/static/favicon.png","description":"custom model","suggestion_prompts":null,"tags":[],"capabilities":{"vision":true,"file_upload":true,"web_search":true,"image_generation":true,"video_generation":true,"code_interpreter":false,"citations":false,"status_updates":false,"usage":false},"knowledge":["6dfc33ed-e63f-42a7-9a65-d76f73711102","kb_id_2"]},"params":{"system":"custom prompt","temperature":0.1},"access_control":{"read":{"group_ids":[],"user_ids":[]},"write":{"group_ids":[],"user_ids":[]}}}'


Update Custom Model

curl 'https://safuapi.prod.secfdg.net/safugpt/api/v1/models/model/update?id=custom-model' \
 
  -H 'authorization: Bearer <safuapi_token>' \
 
  -H 'content-type: application/json' \
 
  --data-raw '{"id":"custom-model","base_model_id":"openai/gpt-4.1","name":"Custom Model","meta":{"profile_image_url":"<base64_url>","description":"custom model","capabilities":{"vision":true,"file_upload":true,"web_search":true,"image_generation":true,"video_generation":true,"code_interpreter":false,"citations":false,"status_updates":false,"usage":false},"knowledge":[],"suggestion_prompts":null,"tags":[]},"params":{"system":"custom prompt","temperature":0.1},"access_control":{"read":{"group_ids":[],"user_ids":[]},"write":{"group_ids":[],"user_ids":[]}},"is_active":true}'


Update Custom Model V2

Use the knowledge base ID instead of the full object, unlike in v1.

Note: v2 support full object and id as input in the array.

meta.knowledge (array of ids) = ["6dfc33ed-e63f-42a7-9a65-d76f73711102", "kb_id_2", {"id": "6dfc33ed-e63f-42a7-9a65-d76f73711102", ...}]

curl 'https://safuapi.prod.secfdg.net/safugpt/api/v2/models/model/update?id=custom-model' \
 
  -H 'authorization: Bearer <safuapi_token>' \
 
  -H 'content-type: application/json' \
 
  --data-raw '{"id":"custom-model","base_model_id":"openai/gpt-4.1","name":"Custom Model","meta":{"profile_image_url":"<base64_url>","description":"custom model","capabilities":{"vision":true,"file_upload":true,"web_search":true,"image_generation":true,"video_generation":true,"code_interpreter":false,"citations":false,"status_updates":false,"usage":false},"knowledge":[],"suggestion_prompts":null,"tags":[]},"params":{"system":"custom prompt","temperature":0.1},"access_control":{"read":{"group_ids":[],"user_ids":[]},"write":{"group_ids":[],"user_ids":["6dfc33ed-e63f-42a7-9a65-d76f73711102","kb_id_2"]}},"is_active":true}'


Delete Custom Model

curl 'https://safuapi.prod.secfdg.net/safugpt/api/v1/models/model/delete?id=custom-model' \
 
  -X 'DELETE' \
 
  -H 'authorization: Bearer <safuapi_token>' \
 
  -H 'content-type: application/json'

  Created by ky.o@binance.com, last modified on Sept 05, 2025
1. Default RAG Template:


Default RAG Template
### Task:
Respond to the user query using the provided context, incorporating inline citations in the format [id] **only when the <source> tag includes an explicit id attribute** (e.g., <source id="1">).
 
### Guidelines:
- If you don't know the answer, clearly state that.
- If uncertain, ask the user for clarification.
- Respond in the same language as the user's query.
- If the context is unreadable or of poor quality, inform the user and provide the best possible answer.
- If the answer isn't present in the context but you possess the knowledge, explain this to the user and provide the answer using your own understanding.
- **Only include inline citations using [id] (e.g., [1], [2]) when the <source> tag includes an id attribute.**
- Do not cite if the <source> tag does not contain an id attribute.
- Do not use XML tags in your response.
- Ensure citations are concise and directly related to the information provided.
 
### Example of Citation:
If the user asks about a specific topic and the information is found in a source with a provided id attribute, the response should include the citation like in the following example:
* "According to the study, the proposed method increases efficiency by 20% [1]."
 
### Output:
Provide a clear and direct response to the user's query, including inline citations in the format [id] only when the <source> tag with id attribute is present in the context.
 
<context>
{{CONTEXT}}
</context>
 
<user_query>
{{QUERY}}
</user_query>
2. Fine Tuning through Custom Model's System Prompt

NOTE: Add #RAG_TEMPLATE to the first line of the system prompt of the custom model to override the system default RAG template

Example
#RAG_TEMPLATE
 
### Task:
- NEVER use internal knowledge to response URL or Links.
...
 
<context>
{{CONTEXT}}
</context>
 
<user_query>
{{QUERY}}
</user_query>
⚠️ ATTENTION:

The placeholder {{QUERY}} is used to represent the user’s input or request.

The placeholder {{CONTEXT}} is used to represent the knowledge base or supporting information available.

These placeholders (with double curly braces) will be dynamically substituted at runtime with their actual values.

You only need to declare this placeholder format once in the system prompt, because repeating it unnecessary increases the context length and may impact overall efficiency.