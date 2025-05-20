import zmq
import pickle

from config import ZMQ_PORT_BREED_INFO_FRONTEND


# Breed data
breed_data = [
    (
        "Cat",
        "Abyssinian",
        "The Abyssinian is a medium-sized cat with a lean, muscular body and a short coat, known for being extremely active and playful.",
        "https://en.wikipedia.org/wiki/Abyssinian",
    ),
    (
        "Dog",
        "American Bulldog",
        "A strong, muscular dog known for its loyalty and protective nature.",
        "https://en.wikipedia.org/wiki/American_Bulldog",
    ),
    (
        "Dog",
        "American Pitbull Terrier",
        "Energetic and intelligent, often misunderstood but very loyal.",
        "https://en.wikipedia.org/wiki/American_Pit_Bull_Terrier",
    ),
    (
        "Dog",
        "Basset Hound",
        "Low-slung, long-eared dog with a great sense of smell.",
        "https://en.wikipedia.org/wiki/Basset_Hound",
    ),
    (
        "Dog",
        "Beagle",
        "Friendly, curious, and great with families.",
        "https://en.wikipedia.org/wiki/Beagle",
    ),
    (
        "Cat",
        "Bengal",
        "Wild-looking domestic cat with a leopard-like coat.",
        "https://en.wikipedia.org/wiki/Bengal_cat",
    ),
    (
        "Cat",
        "Birman",
        "Affectionate and gentle with striking blue eyes.",
        "https://en.wikipedia.org/wiki/Birman",
    ),
    (
        "Cat",
        "Bombay",
        "Sleek black coat and copper eyes, known as the 'mini-panther'.",
        "https://en.wikipedia.org/wiki/Bombay_cat",
    ),
    (
        "Dog",
        "Boxer",
        "Energetic and playful, great with kids.",
        "https://en.wikipedia.org/wiki/Boxer_(dog)",
    ),
    (
        "Cat",
        "British Shorthair",
        "Calm and easygoing with a plush coat.",
        "https://en.wikipedia.org/wiki/British_Shorthair",
    ),
    (
        "Dog",
        "Chihuahua",
        "Tiny but full of personality.",
        "https://en.wikipedia.org/wiki/Chihuahua_(dog)",
    ),
    (
        "Cat",
        "Egyptian Mau",
        "Spotted coat and known for speed.",
        "https://en.wikipedia.org/wiki/Egyptian_Mau",
    ),
    (
        "Dog",
        "English Cocker Spaniel",
        "Happy and affectionate with a silky coat.",
        "https://en.wikipedia.org/wiki/English_Cocker_Spaniel",
    ),
    (
        "Dog",
        "English Setter",
        "Gentle and friendly with a speckled coat.",
        "https://en.wikipedia.org/wiki/English_Setter",
    ),
    (
        "Dog",
        "German Shorthaired",
        "Versatile hunting dog, energetic and smart.",
        "https://en.wikipedia.org/wiki/German_Shorthaired_Pointer",
    ),
    (
        "Dog",
        "Great Pyrenees",
        "Large, calm, and protective.",
        "https://en.wikipedia.org/wiki/Great_Pyrenees",
    ),
    (
        "Dog",
        "Havanese",
        "Small and sturdy with a silky coat.",
        "https://en.wikipedia.org/wiki/Havanese",
    ),
    (
        "Dog",
        "Japanese Chin",
        "Elegant and charming lapdog.",
        "https://en.wikipedia.org/wiki/Japanese_Chin",
    ),
    (
        "Dog",
        "Keeshond",
        "Fluffy and friendly with a fox-like face.",
        "https://en.wikipedia.org/wiki/Keeshond",
    ),
    (
        "Dog",
        "Leonberger",
        "Giant and gentle, great family dog.",
        "https://en.wikipedia.org/wiki/Leonberger",
    ),
    (
        "Cat",
        "Maine Coon",
        "Large and sociable with a bushy tail.",
        "https://en.wikipedia.org/wiki/Maine_Coon",
    ),
    (
        "Dog",
        "Miniature Pinscher",
        "Fearless and energetic, known as the 'King of Toys'.",
        "https://en.wikipedia.org/wiki/Miniature_Pinscher",
    ),
    (
        "Dog",
        "Newfoundland",
        "Massive and gentle, great swimmer.",
        "https://en.wikipedia.org/wiki/Newfoundland_(dog)",
    ),
    (
        "Cat",
        "Persian",
        "Long-haired and calm with a flat face.",
        "https://en.wikipedia.org/wiki/Persian_cat",
    ),
    (
        "Dog",
        "Pomeranian",
        "Tiny and fluffy with a bold personality.",
        "https://en.wikipedia.org/wiki/Pomeranian_(dog)",
    ),
    (
        "Dog",
        "Pug",
        "Charming and mischievous with a wrinkled face.",
        "https://en.wikipedia.org/wiki/Pug",
    ),
    (
        "Cat",
        "Ragdoll",
        "Docile and affectionate, often goes limp when held.",
        "https://en.wikipedia.org/wiki/Ragdoll",
    ),
    (
        "Cat",
        "Russian Blue",
        "Elegant and shy with a silvery coat.",
        "https://en.wikipedia.org/wiki/Russian_Blue",
    ),
    (
        "Dog",
        "Saint Bernard",
        "Massive and gentle, known for rescue work.",
        "https://en.wikipedia.org/wiki/Saint_Bernard_(dog)",
    ),
    (
        "Dog",
        "Samoyed",
        "Fluffy and friendly with a perpetual smile.",
        "https://en.wikipedia.org/wiki/Samoyed_(dog)",
    ),
    (
        "Dog",
        "Scottish Terrier",
        "Independent and dignified with a wiry coat.",
        "https://en.wikipedia.org/wiki/Scottish_Terrier",
    ),
    (
        "Dog",
        "Shiba Inu",
        "Alert and agile with a fox-like appearance.",
        "https://en.wikipedia.org/wiki/Shiba_Inu",
    ),
    (
        "Cat",
        "Siamese",
        "Vocal and affectionate with striking blue eyes.",
        "https://en.wikipedia.org/wiki/Siamese_cat",
    ),
    (
        "Cat",
        "Sphynx",
        "Hairless and warm with a curious nature.",
        "https://en.wikipedia.org/wiki/Sphynx_cat",
    ),
    (
        "Dog",
        "Staffordshire Bull Terrier",
        "Strong and loving, great with children.",
        "https://en.wikipedia.org/wiki/Staffordshire_Bull_Terrier",
    ),
    (
        "Dog",
        "Wheaten Terrier",
        "Soft-coated and friendly.",
        "https://en.wikipedia.org/wiki/Soft-coated_Wheaten_Terrier",
    ),
    (
        "Dog",
        "Yorkshire Terrier",
        "Tiny and brave with a silky coat.",
        "https://en.wikipedia.org/wiki/Yorkshire_Terrier",
    ),
]

# ZeroMQ server
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(f"tcp://*:{ZMQ_PORT_BREED_INFO_FRONTEND}")

print("Microservice is running...")

while True:
    message = socket.recv()
    request = pickle.loads(message)

    print("=============================================")
    if "class" in request:
        class_id = request["class"]
        print("Received class request for class ID:", class_id)
        if 0 <= class_id < len(breed_data):
            species, breed, description, link = breed_data[class_id]
            response = {
                "species": species,
                "breed": breed,
                "description": description,
                "link": link,
            }
            print(f"Sending Response: {response}")
        else:
            response = {
                "error": {
                    "short": "Invalid ID",
                    "message": f"Class ID {class_id} is out of range.",
                    "suggestion": "Valid class IDs are integers from 0 to 36.",
                }
            }
            print(f"Sending Error response: {response}")

    elif "list" in request:
        print("Received list request")
        response = {
            "list": [f"{species} - {breed}" for species, breed, _, _ in breed_data]
        }
        print(f"Response: {response}")
    else:
        response = {"error": "Invalid request format"}

    socket.send(pickle.dumps(response))
