

* Most Encryption is A -> B
* What about encryption to public stream
* Hide recipients

# Project Goals

* Social web discussion platform like Twitter or Buzz
* How can we use these services to do secure discussion, given an evil service
* I want to send a secure message to a group of friends.

"Threat model"
# What evil can Twitter do?
	* DOS & DDOS
		* Twitter can just refuse to post your message
		* Multiple accounts sending tweets with group's identifier
		* Can't defend against this.
	* Replay a message
		* This is bad if you use encrypted messages to send missiles
		* Time stamping can defend
	* Alter a message
		* very bad
	* Create a new secure tweet
		* Very bad
		* Our protocol must make it impossible for twitter or anyone else to send a secure tweet that they should not be able to send
	* Change author
		* Must do signing
		* This can be added into our protocol
	* Change tweet time
		* Timestamp in the message can be compared against Twitter's timestamp. If significantly different, then twitter is being evil
		* Always trust timestamp in the message. Not twitter
		
* What can a bystander learn?
	* I'm sending a secure message? 
		* Yes
		* Revealing you are a group member
		* This is fundamental to Twitter being a public feed.
		* Everyone knows I'm sending a secure tweet
	* Who I'm sending a message to?
		* No
		* WOn't group
		* Won't direct recipients
	* That certain messages are sent to the same group?
		* Maybe
	* Who is in a group
		* If a group title (hash secret) is discovered, group members are not immediately obvious
		* It is an opt-in, so there is no direct derivation from group tag name to members
		* Although any group member who has posted to the group is theoretically discoverable
		* They can't necessarily trust that those people actually posted the message because twitter is evil

# Security Considerations:
* Identification: How will a friend know i've sent them something
* Privacy: Only my friends can read the message
* Integrity: A friend can know that I sent this secure message
			
# Identification
* Twitter has concept of hash tags (#comp527-dudes)
* What if only my friends know of this hashtag
* We can then hash this hashtag
* "comp527-dudes" => "IQHyjdQb8ky8OEc0aY2/0qXDP/w="
* Friends can all do this hashing
* No one else knows it
* What if we start our tweet like:
	IQHyjdQb8ky8OEc0aY2/0qXDP/w= Hey guys, good luck on the presentations!
* Now anyone can see the hash of our hashtag, but no one knows who that is
* BUT, if I send multiple messages, then 
	IQHyjdQb8ky8OEc0aY2/0qXDP/w= Hi guyz
	IQHyjdQb8ky8OEc0aY2/0qXDP/w= I meant "Hi guys"
* Now bystander nows that these two messages were sent to the same group
* Is this terribly bad?
	* No, but we would like to make it hard to know that two messages are to the same group
* To fix this:
	* Use multiple hash routines: MD5, SHA128, SHA256, etc
		* Now a group name has X different identifiers
		* Still will have messages sent to same identifiers, since X+1 messages can be sent
	* MAC with N different seeds known to everyone
		* Same problem as multiple hash routines
	* MAC with next seed in cipher-text message
		* Guaranteed to be difficult to find multiple messages to same group
		* What if twitter doesn't post one of the tweets
		* Fail
	* MAC with epoch as the seed
		* That way, only messages within the same epoch will have same identifier
		* Now only can search for messages within an epoch
		* Twitter fiddling with timestamps isn't a real problem
		* Defends against DDOS
	* MAC with seed in plaintext of tweet
		* Twitter can muck with this
		* Search now has to compute a MAC for every tweet
	* Balance between ease of search, and maximum privacy
	* We chose multiple hash routines
* Only take subset of hash
	* Manageable number of results
	* Collisions are good
		* Multiple groups have higher likelihood to collide, so some groups will "identify" the same
	* Gives away less information about the underlying group name
		* Somewhat prevents reverse lookup tables

# Encryption

* Private key/ Public key
	* Offline share private and public keys.
	* More expensive decryption
	* Can post to group without reading
	* Does not scale
	* Easier shared secret
* Shared secret
* Initially decided on offline shared secret distribution
* What if shared secret is also group name
	* Being inducted into the group means you only need to get the private group name. It's the identifier and the key!

# Encryption Scheme

	hash_alg = random hash algorithm

	identifier = base64(hash_alg(group_secret))
	short_identifier = truncate(identifier)

	msg = plain_text + timestamp()
	cipher = base64(AES(group_secret, msg))

	output = short_identifier + cipher

# Integrity

* If you find a tweet with your identifier, it's a possible message to you
* Decrypt the cipher-text
* All plain text messages have a message at the beginning identifying char140 encryption
* Use this to see if this message was encrypted with our group name
* If not, was not meant for us, or it has been tampered with
* Check timestamp
* Our system relies on authorship via Twitter usernames
* Twitter can change these
* Simple answer: don't rely on authors. Only care about messages being posted to groups, not who said it
* Real solution: sign the messages with the author
	* Requires a separate private key public key exchange system

# What about those pesky 140 characters

* Arbitrary limit makes encryption kind of a bitch
* Couple solutions
	* Use Buzz
	* Use Unicode characters
		* Instead of base64 encoding, we can unicode encode
		* Doesn't help much
	* Split up the message
		* Identifier at start of each message
		* Rest of tweet is that segment of cipher-text
		* Identifier at end to mark last tweet in a message
		* If twitter removes a single message, problem, but this is just DOS
	* Use bit.ly
		* Easy way to get around 140 limit
		* Just use the tweet to post the identifier and a link to a bit.ly url
		* URL redirects to encrypted cipher-text
		* Anyone can get these bit.ly urls, but everything is still encrypted
	* Originally our main focus, but
	* Not as fun a problem as the other stuff we later discovered

# Implementation

* Python script
* Can generate a tweet from a plain text message and a group name
* Can decrypt
* Hosted on github:
	* git clone git://github.com/dbachrach/char140.git