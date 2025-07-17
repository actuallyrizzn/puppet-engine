# Third-Party Licenses

This document lists the third-party libraries and components used in Puppet Engine along with their respective licenses.

## Overview

Puppet Engine uses various open-source libraries and components. This document provides transparency about the licenses of these dependencies and ensures compliance with their terms.

## Python Dependencies

### Core Dependencies

| Package | Version | License | Description |
|---------|---------|---------|-------------|
| fastapi | 0.104.1 | MIT | Modern, fast web framework for building APIs |
| uvicorn | 0.24.0 | BSD | ASGI server implementation |
| pydantic | 2.5.0 | MIT | Data validation using Python type annotations |
| aiohttp | 3.9.1 | Apache 2.0 | Async HTTP client/server framework |
| aiosqlite | 0.19.0 | MIT | Async interface for SQLite |
| numpy | 1.24.3 | BSD | Numerical computing library |
| sentence-transformers | 2.2.2 | Apache 2.0 | Sentence embeddings and semantic similarity |
| openai | 1.3.7 | MIT | OpenAI API client |
| tweepy | 4.14.0 | MIT | Twitter API client |
| solana | 0.30.2 | Apache 2.0 | Solana blockchain client |
| base58 | 2.1.1 | MIT | Base58 encoding/decoding |
| cryptography | 41.0.7 | Apache 2.0 | Cryptographic recipes and primitives |

### Development Dependencies

| Package | Version | License | Description |
|---------|---------|---------|-------------|
| pytest | 7.4.3 | MIT | Testing framework |
| pytest-asyncio | 0.21.1 | Apache 2.0 | Async support for pytest |
| pytest-cov | 4.1.0 | MIT | Coverage plugin for pytest |
| pytest-mock | 3.12.0 | MIT | Mocking plugin for pytest |
| black | 23.11.0 | MIT | Code formatter |
| isort | 5.12.0 | MIT | Import sorting utility |
| flake8 | 6.1.0 | MIT | Linting tool |
| mypy | 1.7.1 | MIT | Static type checker |
| bandit | 1.7.5 | Apache 2.0 | Security linter |

## License Types

### MIT License

The MIT License is a permissive license that allows for:
- Commercial use
- Modification
- Distribution
- Private use

**Used by**: fastapi, uvicorn, pydantic, aiohttp, aiosqlite, base58, pytest, pytest-cov, pytest-mock, black, isort, flake8, mypy, openai, tweepy

### Apache 2.0 License

The Apache 2.0 License is a permissive license that includes:
- Patent protection
- Commercial use
- Modification
- Distribution
- Private use

**Used by**: aiohttp, sentence-transformers, solana, cryptography, pytest-asyncio, bandit

### BSD License

The BSD License is a permissive license that allows for:
- Commercial use
- Modification
- Distribution
- Private use

**Used by**: uvicorn, numpy

## License Compliance

### Attribution Requirements

Some dependencies require attribution. This section lists those requirements:

#### sentence-transformers (Apache 2.0)
```
Copyright 2019 The sentence-transformers Authors.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

#### solana (Apache 2.0)
```
Copyright 2020 Solana Labs, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### License Compatibility

All third-party dependencies used in Puppet Engine are compatible with the CC-BY-SA 4.0 license under which Puppet Engine is distributed. The permissive nature of MIT, Apache 2.0, and BSD licenses allows for their use in CC-BY-SA licensed projects.

## External Services and APIs

### Twitter API

- **Service**: Twitter API v2
- **License**: Twitter Developer Agreement
- **Usage**: Social media posting and monitoring
- **Terms**: [Twitter Developer Agreement](https://developer.twitter.com/en/developer-terms/agreement-and-policy)

### OpenAI API

- **Service**: OpenAI API
- **License**: OpenAI API Terms of Service
- **Usage**: Language model generation
- **Terms**: [OpenAI API Terms](https://openai.com/api-terms/)

### Grok API

- **Service**: xAI Grok API
- **License**: xAI API Terms of Service
- **Usage**: Alternative language model generation
- **Terms**: [xAI API Terms](https://x.ai/terms)

### Solana Network

- **Service**: Solana blockchain
- **License**: Apache 2.0
- **Usage**: Blockchain transactions and trading
- **Terms**: [Solana Terms](https://solana.com/terms)

### Jupiter Protocol

- **Service**: Jupiter aggregator
- **License**: MIT
- **Usage**: Token swapping and price data
- **Terms**: [Jupiter Terms](https://jup.ag/terms)

## License Verification

### Automated License Checking

We use automated tools to verify license compliance:

```bash
# Check for license compatibility
pip-licenses --format=markdown

# Verify license files
pip-licenses --format=json --with-authors --with-urls --with-description
```

### Manual Verification

All licenses have been manually verified to ensure:
1. **Compatibility** with CC-BY-SA 4.0
2. **Attribution** requirements are met
3. **Usage rights** are properly understood
4. **Terms** are complied with

## License Updates

### Monitoring

We regularly monitor for:
- License changes in dependencies
- New license requirements
- Compliance issues
- Security vulnerabilities

### Update Process

When updating dependencies:
1. **Check license changes** in new versions
2. **Verify compatibility** with our license
3. **Update this document** if needed
4. **Test thoroughly** before deployment

## Compliance Checklist

### For Contributors

- [ ] All new dependencies are compatible with CC-BY-SA 4.0
- [ ] License information is documented here
- [ ] Attribution requirements are met
- [ ] No proprietary or restrictive licenses are included

### For Maintainers

- [ ] Regular license audits are performed
- [ ] Dependencies are kept up to date
- [ ] License compliance is verified
- [ ] This document is maintained

## License Text References

### MIT License (Full Text)

```
MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Apache 2.0 License (Full Text)

```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (which shall not include communications that are clearly marked or
      otherwise designated in writing by the copyright owner as "Not a Contribution").

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to use, reproduce, modify, display, perform,
      sublicense, and distribute the Work and such Derivative Works in
      Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, trademark, patent,
          and attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright notice to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Support. You may choose to offer,
      and to charge a fee for, warranty, support, indemnity or other
      liability obligations and/or rights consistent with this License.
      However, in accepting such obligations, You may act only on Your
      own behalf and on Your sole responsibility, not on behalf of any
      other Contributor, and only if You agree to indemnify, defend, and
      hold each Contributor harmless for any liability incurred by, or
      claims asserted against, such Contributor by reason of your accepting
      any such warranty or additional support.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same page as the copyright notice for easier identification within
      third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

## Contact

For questions about third-party licenses or compliance:

- **Issues**: [GitHub Issues](https://github.com/username/puppet-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/puppet-engine/discussions)
- **Email**: legal@puppet-engine.com

## Updates

This document was last updated on December 19, 2024.

For the most current information about third-party licenses, please check the latest version of this document in the repository. 