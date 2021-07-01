# csv_to_pan

Simple tools to build NGFW configuration snippets from CSV input files


## Example Building Skillets

First, use SLI to create base skillets from each config diff for each step in the desired process:

```bash
(venv39) DFWMACK0AJHTDG:csv_to_pan nembery$ sli diff working/01-base.xml working/02-address-objects-added.xml --offline -of skillet
Skillet Name: <my_skillet>: 
Skillet Label: <my label>: 
Skillet Description: <my description>: 
name: my_skillet
label: my label
description: my description

type: panos

variables:

snippets:
  - name: snippet_1
    xpath: /config/devices/entry[@name="localhost.localdomain"]/device-group/entry[@name="poc-dg"]/address
    element: |-
      <entry name="ip10.0.2.1">
        <ip-netmask>10.0.2.1</ip-netmask>
      </entry>
      
  - name: snippet_2
    xpath: /config/devices/entry[@name="localhost.localdomain"]/device-group/entry[@name="poc-dg"]/address
    element: |-
      <entry name="ip192.168.1.1">
        <ip-netmask>192.168.1.1</ip-netmask>
      </entry>
      
(venv39) DFWMACK0AJHTDG:csv_to_pan nembery$ sli diff working/02-address-objects-added.xml working/03-address-group-added.xml --offline -of skillet
Skillet Name: <my_skillet>: add_address_groups
Skillet Label: <my label>: Add Address Groups
Skillet Description: <my description>: Assigns IPs to Groups
name: add_address_groups
label: Add Address Groups
description: Assigns IPs to Groups

type: panos

variables:

snippets:
  - name: snippet_1
    xpath: /config/devices/entry[@name="localhost.localdomain"]/device-group/entry[@name="poc-dg"]
    element: |-
      <address-group>
        <entry name="SOURCE_GROUP1">
          <static>
            <member>ip10.0.0.1</member>
            <member>ip10.0.2.1</member>
          </static>
        </entry>
        <entry name="DEST_GROUP1">
          <static>
            <member>ip192.168.1.1</member>
          </static>
        </entry>
      </address-group>
      
(venv39) DFWMACK0AJHTDG:csv_to_pan nembery$ sli diff working/03-address-group-added.xml working/04-service-group-added.xml --offline -of skillet
Skillet Name: <my_skillet>: add_service_group
Skillet Label: <my label>: Add Service Group
Skillet Description: <my description>: Adds a service group
name: add_service_group
label: Add Service Group
description: Adds a service group

type: panos

variables:

snippets:
  - name: snippet_1
    xpath: /config/devices/entry[@name="localhost.localdomain"]/device-group/entry[@name="poc-dg"]
    element: |-
      <service-group>
        <entry name="PORT_GROUP1">
          <members>
            <member>service-http</member>
          </members>
        </entry>
      </service-group>
      
(venv39) DFWMACK0AJHTDG:csv_to_pan nembery$ sli diff working/04-service-group-added.xml working/05-security-rule-added.xml --offline -of skillet
Skillet Name: <my_skillet>: add_security_rule
Skillet Label: <my label>: Add Security Rule
Skillet Description: <my description>: Adds a security rule
name: add_security_rule
label: Add Security Rule
description: Adds a security rule

type: panos

variables:

snippets:
  - name: snippet_1
    xpath: /config/devices/entry[@name="localhost.localdomain"]/device-group/entry[@name="poc-dg"]
    element: |-
      <pre-rulebase>
        <security>
          <rules>
            <entry name="test rule 1">
              <from>
                <member>any</member>
              </from>
              <source>
                <member>SOURCE_GROUP1</member>
              </source>
              <to>
                <member>any</member>
              </to>
              <destination>
                <member>DEST_GROUP1</member>
              </destination>
              <application>
                <member>web-browsing</member>
              </application>
              <service>
                <member>PORT_GROUP1</member>
              </service>
              <action>allow</action>
              <profile-setting>
                <group>
                  <member>default</member>
                </group>
              </profile-setting>
              <log-setting>default</log-setting>
              <description>test comment</description>
              <group-tag>SectionTitle2</group-tag>
            </entry>
          </rules>
        </security>
      </pre-rulebase>
```

Second, edit the xpaths and elements to assign variables

```bash
name: add_address_objects
label: Add Address Objects
description: Adds an IP Address Entry

type: panos

variables:
  - name: device_group
    default: poc-dg
    description: Device Group
    type_hint: text
  - name: ip_address
    default: 192.168.254.254
    description: IP Address
    type_hint: ip_address
snippets:
  - name: snippet_1
    xpath: /config/devices/entry[@name="localhost.localdomain"]/device-group/entry[@name="poc-dg"]/address
    element: |-
      <entry name="ip{{ ip_address }}">
        <ip-netmask>{{ ip_address }}</ip-netmask>
      </entry>
```

Third, create simple logic to read the input file and assign variables

