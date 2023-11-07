# Speaker-Verification-System-For-Biometric-Authentication
This system designed to identify and authenticate individuals based on their unique vocal characteristics. It utilizes advanced algorithms and signal processing techniques to analyze and compare voice samples for verification purposes.
The system typically consists of two main stages: enrollment and verification. During the enrollment stage, the user's voice is recorded and analyzed to extract distinctive features, such as pitch, frequency, and duration patterns. These features are then converted into a digital voiceprint or template, which serves as a reference for future verification.
In the verification stage, when a user attempts to gain access to a system or service, their voice is captured and compared against the stored voiceprint. The system performs a series of sophisticated algorithms to measure the similarity between the newly captured voice and the stored template. If the similarity exceeds a predefined threshold, the user is granted access. Otherwise, the authentication is denied.
# journal paper link : http://www.ijnrd.org/papers/IJNRD2306536.pdf


  implementation video:
  
  https://drive.google.com/file/d/1RJNzaAxawP-3SR5AEti-E2G5kQANEWy9/view?usp=sharing

  analysis with various optimizers

    
  performance measure:

    
  accruracy(optimizer= sgd):(best)
  ![sgdA](https://github.com/Iama-king/speaker-verification-system-for-biometric-authentication/assets/87493642/3237a717-d9c0-45cb-8f3d-aff2bf4afa15)
  
  accuracy(optimizer=adagrad):
  
  ![adagradA](https://github.com/Iama-king/speaker-verification-system-for-biometric-authentication/assets/87493642/19f8d76d-ca41-49db-9c66-6a67d64b9766)

  accuracy(optimizer=adam):
  ![adamA](https://github.com/Iama-king/speaker-verification-system-for-biometric-authentication/assets/87493642/ce52e966-0663-47fa-8ca8-051640946f5d)

  ERR caluculation(to determine acceptance threshold ) x=98
  ![sp2](https://github.com/Iama-king/speaker-verification-system-for-biometric-authentication/assets/87493642/d0132601-9326-4170-b6ee-0111f682a09b)

