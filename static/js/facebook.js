/*********************************************************************************
**
** The MIT License
**
** Copyright (c) 2009 Luis C. Cruz
** 
** Permission is hereby granted, free of charge, to any person obtaining a copy
** of this software and associated documentation files (the "Software"), to deal
** in the Software without restriction, including without limitation the rights
** to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
** copies of the Software, and to permit persons to whom the Software is
** furnished to do so, subject to the following conditions:
** 
** The above copyright notice and this permission notice shall be included in
** all copies or substantial portions of the Software.
** 
** THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
** IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
** FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
** AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
** LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
** OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
** THE SOFTWARE.
**
*********************************************************************************/

/**
* Constructor
**/
function Facebook(){
    
}

/**
* This class define a Facebook user.
*
* At this momento only json format for response is implemented and uses
* JQuery to do ajax request and others.
* This class don't log in a the user, the session should be actived.
**/
prototype = {    
    // Urls for retrieve facebook data.
    url_profile: null,
    url_stream: null,
    url_update: null,
    
    // this field will be called when the response is not valid params xhr, options and element
    callback_error: null,
    callback_success: null,
    
    element: null,
    
    // functions
    
    /**
    * @param element is the html element.
    * @error if url_profile is not defined 
    *
    * This function generates the elements inside the param element
    * using the data obtained by the request.
    * And this should be the first function called.
    **/
    get_profile: function(element){
        this.element = $(element);
        if (this.url_profile == null)
            throw new Error("URL for profile is not defined.");
        $.ajax({type: "GET",
                url: this.url_profile,
                dataType: "json",
                success: this._generate_element,
                error: this._on_error});
    },
    
    /**
    * This function should be the callback for get_profile function.
    **/
    _generate_element: function(data, textStatus){
        var instance = get_facebook_object();
        
        // creating the base html structure
        var div = $("<div><div id='profile-facebook'></div><div id='news'></div>");
        
        var profile = "<img src='" + data["pic_small"] + "' width='50' height='50'/>";
        profile += "<div style='display:inline-block; padding:15px;'><p class='facebook-user'></p><p class='facebook-name'></p></div>";
        profile = $(profile);
        profile.find(".facebook-user").text(data["name"]);
        
        div.find("#profile-facebook").append(profile);
        
        instance.element.html(div);
        
        if (instance.callback_success)
            instance.callback_success(this, instance.element);
    },
    
    /**
    * This function should be callback for every request did by an object
    * instance of this class.
    * Clear the element field and call the callback function with the params.
    **/
    _on_error: function(xhr, textStatus, thrownError){
        var instance = get_facebook_object();
        if (xhr && xhr.readyState > 1){
            var element = $(instance.element);
            element.html("");
            if (instance.callback_error)
                instance.callback_error(xhr, instance.element);
        }
    },
    
    load_stream: function(){
        if (this.url_stream == null)
            throw new Error("URL for timeline is not defined.");
        $.ajax({type: "GET",
                url: this.url_stream,
                dataType: "json",
                success: this._generate_stream,
                error: this._on_error});
    },
    
    _generate_stream: function(data, textStatus){
        if (data.redirect){
            $(location).attr("href", data.url);
        }else{
            var instance = get_facebook_object();
            var posts = data.posts;
            var profiles = data.profiles;
            
            var element = instance.element.find("#news").html("");
            var post = null;
            var profile = null;
            
            for (index in posts){
                post = posts[index];
                profile = instance._get_profile(profiles, post.source_id);
                element.append(instance._generate_post(post, profile));
            }
            
            if (instance.callback_success)
                instance.callback_success(this, instance.element);
        }
    },
    
    _get_profile: function(profiles, id){
        for (index in profiles)
            if (profiles[index].id == id)
                return profiles[index]
        return null;
    },
    
    _generate_post: function(post, profile){
        var time = new Date();
        time.setTime(post.created_time);
        
        var html = "<div style='border: 1px solid white; padding: 10px;'><div><img src='" + profile.pic_square + "' width='50' height='50'/>";
        html += "<p class='post-facebook'></p></div>"; // screen name
        html += "<div> <p class='facebook-text'></p>" // text
        html += "<p> At " + time.getHours() + ":" + time.getMinutes() + ":" + time.getSeconds() + "</p></div></div>";
        html = $(html);
        
        html.find(".post-facebook").text(profile.name);
        html.find(".facebook-text").text(post.message);
        return html;
    },
    
    send_status: function(text){
        if (this.url_update == null)
            throw new Error("URL for update is not defined.");
        if (text != ""){
            $.ajax({type: "POST",
                url: this.url_update,
                data: {status: text},
                dataType: "json",
                success: this._post_sent,
                error: this._on_error});
        }
    },
    
    _post_sent: function(data, textStatus){
        var instance = get_facebook_object();
        var element = instance.element.find("#news");
        
        if (data.redirect){
            $(location).attr("href", data.url);
        } else if (!data.success){
            element.prepend("<p style='color:red'>An error ocurred try again</p>");
            if (instance.callback_success)
                instance.callback_success(this, instance.element);
        } else {
            instance.load_stream();
        }
    },
};

$.extend(Facebook.prototype, prototype);

function get_facebook_object(){
    return facebook_user;
}

// Global variable for a Twitter object instance
var facebook_user = new Facebook();